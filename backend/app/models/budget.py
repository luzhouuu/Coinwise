"""Budget goal data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BudgetGoalBase(BaseModel):
    """Base budget goal fields."""

    category_id: int = Field(..., description="Category ID")
    amount: float = Field(..., gt=0, description="Budget amount")
    is_recurring: bool = Field(default=True, description="Apply to future months")


class BudgetGoalCreate(BudgetGoalBase):
    """Create budget goal request."""

    year: int = Field(..., ge=2020, le=2100, description="Budget year")
    month: int = Field(..., ge=1, le=12, description="Budget month (1-12)")


class BudgetGoalUpdate(BaseModel):
    """Update budget goal request."""

    amount: Optional[float] = Field(None, gt=0, description="New budget amount")
    is_recurring: Optional[bool] = Field(None, description="Apply to future months")


class BudgetGoal(BudgetGoalBase):
    """Budget goal response."""

    id: int
    year: int
    month: int
    category_name: str = Field(..., description="Category name")
    category_color: Optional[str] = Field(None, description="Category color")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetSummaryItem(BaseModel):
    """Budget vs actual for a single category."""

    category_id: int
    category_name: str
    category_color: Optional[str] = None
    budget_amount: float = Field(..., description="Budget limit")
    spent_amount: float = Field(..., description="Actual spending")
    remaining: float = Field(..., description="Remaining budget")
    percentage_used: float = Field(..., description="Percentage of budget used")


class BudgetSummary(BaseModel):
    """Monthly budget summary."""

    year: int
    month: int
    total_budget: float = Field(..., description="Sum of all budgets")
    total_spent: float = Field(..., description="Sum of all spending")
    total_remaining: float = Field(..., description="Remaining budget")
    category_count: int = Field(..., description="Number of categories with budgets")
    items: List[BudgetSummaryItem] = Field(default_factory=list)


class MonthComparisonItem(BaseModel):
    """Spending data for a single month."""

    month: str = Field(..., description="Month label (YYYY-MM)")
    amount: float = Field(..., description="Total spending")


class CategoryComparisonData(BaseModel):
    """Comparison data for a single category."""

    category_name: str
    category_color: Optional[str] = None
    data: List[MonthComparisonItem] = Field(default_factory=list)


class MonthComparisonResponse(BaseModel):
    """Month-over-month comparison response."""

    months: List[str] = Field(..., description="List of months (YYYY-MM)")
    categories: List[CategoryComparisonData] = Field(default_factory=list)
