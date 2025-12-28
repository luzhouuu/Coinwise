"""Budget service for CRUD operations and analytics."""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.database import BudgetGoalModel, CategoryModel, TransactionModel


class BudgetService:
    """Service for budget goal operations."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db

    def get_budgets(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> List[BudgetGoalModel]:
        """Get budget goals with optional filters."""
        query = self.db.query(BudgetGoalModel)

        if year:
            query = query.filter(BudgetGoalModel.year == year)
        if month:
            query = query.filter(BudgetGoalModel.month == month)
        if category_id:
            query = query.filter(BudgetGoalModel.category_id == category_id)

        return query.order_by(BudgetGoalModel.category_id).all()

    def get_budget_by_id(self, budget_id: int) -> Optional[BudgetGoalModel]:
        """Get single budget by ID."""
        return self.db.query(BudgetGoalModel).filter(
            BudgetGoalModel.id == budget_id
        ).first()

    def get_budget_by_category_month(
        self,
        category_id: int,
        year: int,
        month: int,
    ) -> Optional[BudgetGoalModel]:
        """Get budget for specific category and month."""
        return self.db.query(BudgetGoalModel).filter(
            and_(
                BudgetGoalModel.category_id == category_id,
                BudgetGoalModel.year == year,
                BudgetGoalModel.month == month,
            )
        ).first()

    def create_budget(
        self,
        category_id: int,
        year: int,
        month: int,
        amount: float,
        is_recurring: bool = True,
    ) -> BudgetGoalModel:
        """Create a new budget goal."""
        budget = BudgetGoalModel(
            category_id=category_id,
            year=year,
            month=month,
            amount=amount,
            is_recurring=1 if is_recurring else 0,
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def update_budget(
        self,
        budget_id: int,
        amount: Optional[float] = None,
        is_recurring: Optional[bool] = None,
    ) -> Optional[BudgetGoalModel]:
        """Update an existing budget goal."""
        budget = self.get_budget_by_id(budget_id)
        if not budget:
            return None

        if amount is not None:
            budget.amount = amount
        if is_recurring is not None:
            budget.is_recurring = 1 if is_recurring else 0

        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete_budget(self, budget_id: int) -> bool:
        """Delete a budget goal."""
        budget = self.get_budget_by_id(budget_id)
        if not budget:
            return False

        self.db.delete(budget)
        self.db.commit()
        return True

    def get_budget_summary(self, year: int, month: int) -> dict:
        """Get budget vs actual spending summary for a month."""
        # Get start and end of month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Get all budgets for this month
        budgets = self.get_budgets(year=year, month=month)

        # Get spending by category for this month
        spending_query = (
            self.db.query(
                TransactionModel.category_id,
                func.sum(TransactionModel.amount).label("spent"),
            )
            .filter(
                and_(
                    TransactionModel.transaction_date >= start_date,
                    TransactionModel.transaction_date < end_date,
                    TransactionModel.transaction_type == "withdrawal",
                )
            )
            .group_by(TransactionModel.category_id)
        )
        spending_by_category = {r.category_id: abs(r.spent) for r in spending_query.all()}

        # Build summary items
        items = []
        total_budget = 0
        total_spent = 0

        for budget in budgets:
            category = self.db.query(CategoryModel).filter(
                CategoryModel.id == budget.category_id
            ).first()

            spent = spending_by_category.get(budget.category_id, 0)
            remaining = budget.amount - spent
            percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0

            items.append({
                "category_id": budget.category_id,
                "category_name": category.name if category else "Unknown",
                "category_color": category.color if category else None,
                "budget_amount": budget.amount,
                "spent_amount": spent,
                "remaining": remaining,
                "percentage_used": round(percentage, 1),
            })

            total_budget += budget.amount
            total_spent += spent

        return {
            "year": year,
            "month": month,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_remaining": total_budget - total_spent,
            "category_count": len(budgets),
            "items": items,
        }

    def get_month_comparison(self, months: int = 3) -> dict:
        """Get spending comparison for last N months."""
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # Generate list of months to compare
        month_list = []
        for i in range(months - 1, -1, -1):
            m = current_month - i
            y = current_year
            while m <= 0:
                m += 12
                y -= 1
            month_list.append((y, m))

        month_labels = [f"{y}-{m:02d}" for y, m in month_list]

        # Get all categories with transactions
        categories = self.db.query(CategoryModel).all()

        # Get spending data for each category and month
        category_data = []
        for category in categories:
            data = []
            for y, m in month_list:
                start_date = datetime(y, m, 1)
                if m == 12:
                    end_date = datetime(y + 1, 1, 1)
                else:
                    end_date = datetime(y, m + 1, 1)

                spent = (
                    self.db.query(func.sum(TransactionModel.amount))
                    .filter(
                        and_(
                            TransactionModel.category_id == category.id,
                            TransactionModel.transaction_date >= start_date,
                            TransactionModel.transaction_date < end_date,
                            TransactionModel.transaction_type == "withdrawal",
                        )
                    )
                    .scalar()
                )
                data.append({
                    "month": f"{y}-{m:02d}",
                    "amount": abs(spent) if spent else 0,
                })

            # Only include categories with spending
            if any(d["amount"] > 0 for d in data):
                category_data.append({
                    "category_name": category.name,
                    "category_color": category.color,
                    "data": data,
                })

        return {
            "months": month_labels,
            "categories": category_data,
        }

    def copy_recurring_budgets(self, to_year: int, to_month: int) -> int:
        """Copy recurring budgets from previous month."""
        # Calculate previous month
        if to_month == 1:
            from_year = to_year - 1
            from_month = 12
        else:
            from_year = to_year
            from_month = to_month - 1

        # Get recurring budgets from previous month
        recurring = self.db.query(BudgetGoalModel).filter(
            and_(
                BudgetGoalModel.year == from_year,
                BudgetGoalModel.month == from_month,
                BudgetGoalModel.is_recurring == 1,
            )
        ).all()

        count = 0
        for budget in recurring:
            # Check if budget already exists for target month
            existing = self.get_budget_by_category_month(
                budget.category_id, to_year, to_month
            )
            if not existing:
                self.create_budget(
                    category_id=budget.category_id,
                    year=to_year,
                    month=to_month,
                    amount=budget.amount,
                    is_recurring=True,
                )
                count += 1

        return count
