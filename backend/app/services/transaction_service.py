"""Transaction service for CRUD operations."""

import json
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.database import CategoryModel, TransactionModel


class TransactionService:
    """Service for transaction CRUD operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db

    def get_transactions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "transaction_date",
        sort_order: str = "desc",
    ) -> Tuple[List[TransactionModel], int]:
        """Get paginated transactions with filters."""
        query = self.db.query(TransactionModel)

        # Apply filters
        if start_date:
            query = query.filter(TransactionModel.transaction_date >= start_date)
        if end_date:
            query = query.filter(TransactionModel.transaction_date <= end_date)
        if category_id:
            query = query.filter(TransactionModel.category_id == category_id)
        if transaction_type:
            query = query.filter(TransactionModel.transaction_type == transaction_type)
        if search:
            query = query.filter(
                TransactionModel.description.ilike(f"%{search}%")
            )

        # Get total count
        total = query.count()

        # Apply sorting
        sort_column = getattr(TransactionModel, sort_by, TransactionModel.transaction_date)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Apply pagination
        offset = (page - 1) * page_size
        transactions = query.offset(offset).limit(page_size).all()

        return transactions, total

    def get_transaction_by_id(self, transaction_id: int) -> Optional[TransactionModel]:
        """Get single transaction by ID."""
        return self.db.query(TransactionModel).filter(
            TransactionModel.id == transaction_id
        ).first()

    def create_transaction(
        self,
        transaction_date: datetime,
        amount: float,
        description: str,
        transaction_type: str,
        category_id: Optional[int] = None,
        source_account: Optional[str] = None,
        destination_account: Optional[str] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
        is_manual: bool = True,
        source_email_id: Optional[str] = None,
    ) -> TransactionModel:
        """Create a new transaction."""
        transaction = TransactionModel(
            transaction_date=transaction_date,
            amount=amount,
            description=description,
            transaction_type=transaction_type,
            category_id=category_id,
            source_account=source_account,
            destination_account=destination_account,
            tags=json.dumps(tags) if tags else None,
            notes=notes,
            is_manual=1 if is_manual else 0,
            source_email_id=source_email_id,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update_transaction(
        self,
        transaction_id: int,
        **kwargs,
    ) -> Optional[TransactionModel]:
        """Update an existing transaction."""
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return None

        # Handle tags serialization
        if "tags" in kwargs and kwargs["tags"] is not None:
            kwargs["tags"] = json.dumps(kwargs["tags"])

        for key, value in kwargs.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction."""
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            return False

        self.db.delete(transaction)
        self.db.commit()
        return True

    def check_duplicate(self, source_email_id: str) -> bool:
        """Check if transaction from email already exists."""
        return self.db.query(TransactionModel).filter(
            TransactionModel.source_email_id == source_email_id
        ).first() is not None

    def get_statistics_summary(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        """Get summary statistics for date range."""
        query = self.db.query(TransactionModel).filter(
            and_(
                TransactionModel.transaction_date >= start_date,
                TransactionModel.transaction_date <= end_date,
            )
        )

        total_expense = query.filter(
            TransactionModel.transaction_type == "withdrawal"
        ).with_entities(func.sum(TransactionModel.amount)).scalar() or 0

        total_income = query.filter(
            TransactionModel.transaction_type == "deposit"
        ).with_entities(func.sum(TransactionModel.amount)).scalar() or 0

        transaction_count = query.count()

        return {
            "total_expense": abs(total_expense),
            "total_income": total_income,
            "transaction_count": transaction_count,
            "start_date": start_date.date(),
            "end_date": end_date.date(),
        }

    def get_statistics_by_category(
        self,
        start_date: datetime,
        end_date: datetime,
        transaction_type: str = "withdrawal",
    ) -> List[dict]:
        """Get statistics grouped by category."""
        results = (
            self.db.query(
                CategoryModel.name,
                func.sum(TransactionModel.amount).label("amount"),
                func.count(TransactionModel.id).label("count"),
            )
            .join(TransactionModel, TransactionModel.category_id == CategoryModel.id)
            .filter(
                and_(
                    TransactionModel.transaction_date >= start_date,
                    TransactionModel.transaction_date <= end_date,
                    TransactionModel.transaction_type == transaction_type,
                )
            )
            .group_by(CategoryModel.id)
            .all()
        )

        # Calculate total for percentages
        total = sum(abs(r.amount) for r in results) or 1

        return [
            {
                "category": r.name,
                "amount": abs(r.amount),
                "count": r.count,
                "percentage": round(abs(r.amount) / total * 100, 2),
            }
            for r in results
        ]

    def get_trend_data(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "day",
    ) -> List[dict]:
        """Get trend data for charts, filling in missing periods with zeros."""
        from dateutil.relativedelta import relativedelta

        if granularity == "day":
            date_format = "%Y-%m-%d"
            date_trunc = func.date(TransactionModel.transaction_date)
        elif granularity == "week":
            date_format = "%Y-W%W"
            date_trunc = func.strftime("%Y-W%W", TransactionModel.transaction_date)
        else:  # month
            date_format = "%Y-%m"
            date_trunc = func.strftime("%Y-%m", TransactionModel.transaction_date)

        results = (
            self.db.query(
                date_trunc.label("date"),
                func.sum(TransactionModel.amount).label("amount"),
                func.count(TransactionModel.id).label("count"),
            )
            .filter(
                and_(
                    TransactionModel.transaction_date >= start_date,
                    TransactionModel.transaction_date <= end_date,
                    TransactionModel.transaction_type == "withdrawal",
                )
            )
            .group_by(date_trunc)
            .order_by(date_trunc)
            .all()
        )

        # Convert results to dict for easy lookup
        result_dict = {
            str(r.date): {"amount": abs(r.amount) if r.amount else 0, "count": r.count}
            for r in results
        }

        # Generate all periods and fill in missing ones with zeros
        all_data = []
        if granularity == "month":
            current = datetime(start_date.year, start_date.month, 1)
            end = datetime(end_date.year, end_date.month, 1)
            while current <= end:
                date_key = current.strftime("%Y-%m")
                if date_key in result_dict:
                    all_data.append({
                        "date": date_key,
                        "amount": result_dict[date_key]["amount"],
                        "count": result_dict[date_key]["count"],
                    })
                else:
                    all_data.append({"date": date_key, "amount": 0, "count": 0})
                current += relativedelta(months=1)
        else:
            # For day/week granularity, just return actual results
            all_data = [
                {
                    "date": str(r.date),
                    "amount": abs(r.amount) if r.amount else 0,
                    "count": r.count,
                }
                for r in results
            ]

        return all_data
