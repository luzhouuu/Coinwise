"""Budget goals API router."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import CategoryModel, get_db
from app.models import (
    BudgetGoal,
    BudgetGoalCreate,
    BudgetGoalUpdate,
    BudgetSummary,
    BudgetSummaryItem,
    CategoryComparisonData,
    MonthComparisonItem,
    MonthComparisonResponse,
)
from app.services.budget_service import BudgetService

router = APIRouter()


@router.get("/", response_model=List[BudgetGoal])
async def list_budgets(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
) -> List[BudgetGoal]:
    """List budget goals with optional filters."""
    service = BudgetService(db)
    budgets = service.get_budgets(year=year, month=month, category_id=category_id)

    result = []
    for budget in budgets:
        category = db.query(CategoryModel).filter(
            CategoryModel.id == budget.category_id
        ).first()
        result.append(
            BudgetGoal(
                id=budget.id,
                category_id=budget.category_id,
                category_name=category.name if category else "Unknown",
                category_color=category.color if category else None,
                year=budget.year,
                month=budget.month,
                amount=budget.amount,
                is_recurring=budget.is_recurring == 1,
                created_at=budget.created_at,
                updated_at=budget.updated_at,
            )
        )
    return result


@router.get("/summary", response_model=BudgetSummary)
async def get_budget_summary(
    year: int = Query(..., description="Budget year"),
    month: int = Query(..., ge=1, le=12, description="Budget month"),
    db: Session = Depends(get_db),
) -> BudgetSummary:
    """Get budget vs actual spending summary for a month."""
    service = BudgetService(db)
    summary = service.get_budget_summary(year, month)

    return BudgetSummary(
        year=summary["year"],
        month=summary["month"],
        total_budget=summary["total_budget"],
        total_spent=summary["total_spent"],
        total_remaining=summary["total_remaining"],
        category_count=summary["category_count"],
        items=[
            BudgetSummaryItem(
                category_id=item["category_id"],
                category_name=item["category_name"],
                category_color=item["category_color"],
                budget_amount=item["budget_amount"],
                spent_amount=item["spent_amount"],
                remaining=item["remaining"],
                percentage_used=item["percentage_used"],
            )
            for item in summary["items"]
        ],
    )


@router.get("/comparison", response_model=MonthComparisonResponse)
async def get_month_comparison(
    months: int = Query(3, ge=1, le=12, description="Number of months to compare"),
    db: Session = Depends(get_db),
) -> MonthComparisonResponse:
    """Get month-over-month spending comparison."""
    service = BudgetService(db)
    comparison = service.get_month_comparison(months)

    return MonthComparisonResponse(
        months=comparison["months"],
        categories=[
            CategoryComparisonData(
                category_name=cat["category_name"],
                category_color=cat["category_color"],
                data=[
                    MonthComparisonItem(
                        month=d["month"],
                        amount=d["amount"],
                    )
                    for d in cat["data"]
                ],
            )
            for cat in comparison["categories"]
        ],
    )


@router.get("/{budget_id}", response_model=BudgetGoal)
async def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
) -> BudgetGoal:
    """Get a single budget goal by ID."""
    service = BudgetService(db)
    budget = service.get_budget_by_id(budget_id)

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    category = db.query(CategoryModel).filter(
        CategoryModel.id == budget.category_id
    ).first()

    return BudgetGoal(
        id=budget.id,
        category_id=budget.category_id,
        category_name=category.name if category else "Unknown",
        category_color=category.color if category else None,
        year=budget.year,
        month=budget.month,
        amount=budget.amount,
        is_recurring=budget.is_recurring == 1,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@router.post("/", response_model=BudgetGoal)
async def create_budget(
    data: BudgetGoalCreate,
    db: Session = Depends(get_db),
) -> BudgetGoal:
    """Create a new budget goal."""
    # Check if category exists
    category = db.query(CategoryModel).filter(
        CategoryModel.id == data.category_id
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    service = BudgetService(db)

    # Check if budget already exists for this category and month
    existing = service.get_budget_by_category_month(
        data.category_id, data.year, data.month
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget already exists for this category and month"
        )

    budget = service.create_budget(
        category_id=data.category_id,
        year=data.year,
        month=data.month,
        amount=data.amount,
        is_recurring=data.is_recurring,
    )

    return BudgetGoal(
        id=budget.id,
        category_id=budget.category_id,
        category_name=category.name,
        category_color=category.color,
        year=budget.year,
        month=budget.month,
        amount=budget.amount,
        is_recurring=budget.is_recurring == 1,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@router.put("/{budget_id}", response_model=BudgetGoal)
async def update_budget(
    budget_id: int,
    data: BudgetGoalUpdate,
    db: Session = Depends(get_db),
) -> BudgetGoal:
    """Update an existing budget goal."""
    service = BudgetService(db)
    budget = service.update_budget(
        budget_id=budget_id,
        amount=data.amount,
        is_recurring=data.is_recurring,
    )

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    category = db.query(CategoryModel).filter(
        CategoryModel.id == budget.category_id
    ).first()

    return BudgetGoal(
        id=budget.id,
        category_id=budget.category_id,
        category_name=category.name if category else "Unknown",
        category_color=category.color if category else None,
        year=budget.year,
        month=budget.month,
        amount=budget.amount,
        is_recurring=budget.is_recurring == 1,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
):
    """Delete a budget goal."""
    service = BudgetService(db)
    if not service.delete_budget(budget_id):
        raise HTTPException(status_code=404, detail="Budget not found")

    return {"message": "Budget deleted successfully"}


@router.post("/copy-recurring")
async def copy_recurring_budgets(
    year: int = Query(..., description="Target year"),
    month: int = Query(..., ge=1, le=12, description="Target month"),
    db: Session = Depends(get_db),
):
    """Copy recurring budgets from previous month to target month."""
    service = BudgetService(db)
    count = service.copy_recurring_budgets(year, month)

    return {"message": f"Copied {count} recurring budgets", "count": count}
