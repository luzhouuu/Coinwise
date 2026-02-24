"""Pydantic models for API request/response."""

from app.models.config import (
    BlacklistRule,
    BlacklistRuleCreate,
    BlacklistRulesResponse,
    Category,
    CategoryCreate,
    CategoryRule,
    CategoryRuleCreate,
    CategoryRulesResponse,
    CategoryRuleUpdate,
    EmailAccount,
    EmailAccountCreate,
    EmailAccountUpdate,
)
from app.models.statistics import (
    CategoryStat,
    StatisticsSummary,
    TrendDataPoint,
)
from app.models.budget import (
    BudgetGoal,
    BudgetGoalCreate,
    BudgetGoalUpdate,
    BudgetSummary,
    BudgetSummaryItem,
    CategoryComparisonData,
    MonthComparisonItem,
    MonthComparisonResponse,
)
from app.models.sync import (
    SyncLogMessage,
    SyncStartRequest,
    SyncStatus,
    SyncStatusResponse,
)
from app.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionListResponse,
    TransactionUpdate,
)

__all__ = [
    "Transaction",
    "TransactionCreate",
    "TransactionListResponse",
    "TransactionUpdate",
    "SyncStartRequest",
    "SyncStatus",
    "SyncStatusResponse",
    "SyncLogMessage",
    "EmailAccount",
    "EmailAccountCreate",
    "EmailAccountUpdate",
    "Category",
    "CategoryCreate",
    "CategoryRule",
    "CategoryRuleCreate",
    "CategoryRulesResponse",
    "CategoryRuleUpdate",
    "BlacklistRule",
    "BlacklistRuleCreate",
    "BlacklistRulesResponse",
    "StatisticsSummary",
    "CategoryStat",
    "TrendDataPoint",
    "BudgetGoal",
    "BudgetGoalCreate",
    "BudgetGoalUpdate",
    "BudgetSummary",
    "BudgetSummaryItem",
    "CategoryComparisonData",
    "MonthComparisonItem",
    "MonthComparisonResponse",
]
