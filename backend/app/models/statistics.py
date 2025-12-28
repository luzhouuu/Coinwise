"""Statistics data models."""

from datetime import date as date_type

from pydantic import BaseModel, Field


class StatisticsSummary(BaseModel):
    """Summary statistics for a date range."""

    total_expense: float = Field(..., description="Total expenses")
    total_income: float = Field(..., description="Total income")
    transaction_count: int = Field(..., description="Number of transactions")
    start_date: date_type = Field(..., description="Period start date")
    end_date: date_type = Field(..., description="Period end date")


class CategoryStat(BaseModel):
    """Statistics for a single category."""

    category: str = Field(..., description="Category name")
    amount: float = Field(..., description="Total amount in this category")
    count: int = Field(..., description="Number of transactions")
    percentage: float = Field(..., description="Percentage of total")


class TrendDataPoint(BaseModel):
    """Single data point in trend chart."""

    date: str = Field(..., description="Date label (format depends on granularity)")
    amount: float = Field(..., description="Total amount for this period")
    count: int = Field(..., description="Number of transactions")
