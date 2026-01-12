"""Transactions API router."""

import json
import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Transaction,
    TransactionCreate,
    TransactionListResponse,
    TransactionUpdate,
)
from app.services.transaction_service import TransactionService
from app.services.categorizer import Categorizer

router = APIRouter()


def _model_to_response(model) -> Transaction:
    """Convert database model to response model."""
    tags = []
    if model.tags:
        try:
            tags = json.loads(model.tags)
        except (json.JSONDecodeError, TypeError):
            tags = []

    return Transaction(
        id=model.id,
        transaction_date=model.transaction_date,
        amount=model.amount,
        description=model.description,
        category_id=model.category_id,
        category_name=model.category.name if model.category else None,
        transaction_type=model.transaction_type,
        source_account=model.source_account,
        destination_account=model.destination_account,
        tags=tags,
        notes=model.notes,
        is_manual=bool(model.is_manual),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by type"),
    search: Optional[str] = Query(None, description="Search in description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("transaction_date", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
) -> TransactionListResponse:
    """Get paginated list of transactions with filtering and sorting."""
    service = TransactionService(db)

    transactions, total = service.get_transactions(
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        transaction_type=transaction_type,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return TransactionListResponse(
        data=[_model_to_response(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> Transaction:
    """Get a single transaction by ID."""
    service = TransactionService(db)
    transaction = service.get_transaction_by_id(transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return _model_to_response(transaction)


@router.post("", response_model=Transaction, status_code=201)
async def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
) -> Transaction:
    """Create a new transaction (manual entry)."""
    service = TransactionService(db)

    # Auto-categorize if category not provided
    category_id = data.category_id
    if category_id is None and data.description:
        categorizer = Categorizer(db)
        category_id = categorizer.categorize(data.description)

    transaction = service.create_transaction(
        transaction_date=data.transaction_date,
        amount=data.amount,
        description=data.description,
        transaction_type=data.transaction_type,
        category_id=category_id,
        source_account=data.source_account,
        destination_account=data.destination_account,
        tags=data.tags,
        notes=data.notes,
        is_manual=True,
    )

    return _model_to_response(transaction)


@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
) -> Transaction:
    """Update an existing transaction."""
    service = TransactionService(db)

    update_data = data.model_dump(exclude_unset=True)
    transaction = service.update_transaction(transaction_id, **update_data)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return _model_to_response(transaction)


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Delete a transaction by ID."""
    service = TransactionService(db)
    success = service.delete_transaction(transaction_id)

    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {"message": "Transaction deleted successfully", "id": transaction_id}


@router.get("/duplicates/list")
async def get_duplicates(
    db: Session = Depends(get_db),
) -> dict:
    """Get list of duplicate transactions grouped by date/amount/description."""
    service = TransactionService(db)
    duplicates = service.find_duplicates()
    total_duplicates = sum(group["count"] - 1 for group in duplicates)

    return {
        "groups": duplicates,
        "total_duplicate_records": total_duplicates,
        "groups_count": len(duplicates),
    }


@router.post("/duplicates/clean")
async def clean_duplicates(
    db: Session = Depends(get_db),
) -> dict:
    """Remove duplicate transactions, keeping the oldest one in each group."""
    service = TransactionService(db)
    result = service.clean_duplicates()

    return {
        "message": f"Cleaned {result['deleted']} duplicate records from {result['groups_cleaned']} groups",
        **result,
    }
