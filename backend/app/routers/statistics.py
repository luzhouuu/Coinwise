"""Statistics API router."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import CategoryModel, TransactionModel, get_db
from app.models import CategoryStat, StatisticsSummary, TrendDataPoint
from app.models.config import Category
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.get("/summary", response_model=StatisticsSummary)
async def get_summary(
    start_date: datetime = Query(..., description="Period start date"),
    end_date: datetime = Query(..., description="Period end date"),
    db: Session = Depends(get_db),
) -> StatisticsSummary:
    """Get summary statistics for a date range."""
    service = TransactionService(db)
    stats = service.get_statistics_summary(start_date, end_date)

    return StatisticsSummary(
        total_expense=stats["total_expense"],
        total_income=stats["total_income"],
        transaction_count=stats["transaction_count"],
        start_date=stats["start_date"],
        end_date=stats["end_date"],
    )


@router.get("/by-category", response_model=List[CategoryStat])
async def get_by_category(
    start_date: datetime = Query(..., description="Period start date"),
    end_date: datetime = Query(..., description="Period end date"),
    transaction_type: str = Query("withdrawal", description="Transaction type"),
    db: Session = Depends(get_db),
) -> List[CategoryStat]:
    """Get expense breakdown by category."""
    service = TransactionService(db)
    stats = service.get_statistics_by_category(start_date, end_date, transaction_type)

    return [
        CategoryStat(
            category=s["category"],
            amount=s["amount"],
            count=s["count"],
            percentage=s["percentage"],
        )
        for s in stats
    ]


@router.get("/trend", response_model=List[TrendDataPoint])
async def get_trend(
    start_date: datetime = Query(..., description="Period start date"),
    end_date: datetime = Query(..., description="Period end date"),
    granularity: str = Query(
        "month", description="Aggregation granularity: day, week, month"
    ),
    db: Session = Depends(get_db),
) -> List[TrendDataPoint]:
    """Get expense trend over time."""
    service = TransactionService(db)
    trend_data = service.get_trend_data(start_date, end_date, granularity)

    return [
        TrendDataPoint(
            date=d["date"],
            amount=d["amount"],
            count=d["count"],
        )
        for d in trend_data
    ]


@router.get("/categories", response_model=List[Category])
async def get_categories(
    db: Session = Depends(get_db),
) -> List[Category]:
    """Get all available categories."""
    categories = db.query(CategoryModel).all()
    return [
        Category(
            id=c.id,
            name=c.name,
            icon=c.icon,
            color=c.color,
            parent_id=c.parent_id,
        )
        for c in categories
    ]


@router.get("/latest-month")
async def get_latest_month(
    db: Session = Depends(get_db),
):
    """Get the latest month with transaction data in the database."""
    result = (
        db.query(
            func.strftime('%Y', TransactionModel.transaction_date).label('year'),
            func.strftime('%m', TransactionModel.transaction_date).label('month'),
        )
        .filter(TransactionModel.transaction_type == "withdrawal")
        .order_by(TransactionModel.transaction_date.desc())
        .first()
    )

    if result and result.year and result.month:
        return {"year": int(result.year), "month": int(result.month)}

    now = datetime.now()
    return {"year": now.year, "month": now.month}
