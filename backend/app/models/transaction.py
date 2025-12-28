"""Transaction data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    """Base transaction fields."""

    transaction_date: datetime = Field(..., description="Transaction date")
    amount: float = Field(..., description="Transaction amount")
    description: str = Field(..., description="Transaction description")
    category_id: Optional[int] = Field(None, description="Category ID")
    transaction_type: str = Field(
        ..., description="Transaction type: withdrawal/deposit/transfer"
    )
    source_account: Optional[str] = Field(None, description="Source account name")
    destination_account: Optional[str] = Field(
        None, description="Destination account name"
    )
    tags: List[str] = Field(default_factory=list, description="Transaction tags")
    notes: Optional[str] = Field(None, description="Additional notes")


class TransactionCreate(TransactionBase):
    """Request model for creating a transaction."""

    pass


class TransactionUpdate(BaseModel):
    """Request model for updating a transaction."""

    transaction_date: Optional[datetime] = Field(None, description="Transaction date")
    amount: Optional[float] = Field(None, description="Transaction amount")
    description: Optional[str] = Field(None, description="Transaction description")
    category_id: Optional[int] = Field(None, description="Category ID")
    transaction_type: Optional[str] = Field(None, description="Transaction type")
    source_account: Optional[str] = Field(None, description="Source account name")
    destination_account: Optional[str] = Field(None, description="Destination account")
    tags: Optional[List[str]] = Field(None, description="Transaction tags")
    notes: Optional[str] = Field(None, description="Additional notes")


class Transaction(TransactionBase):
    """Transaction response model."""

    id: int = Field(..., description="Transaction ID")
    category_name: Optional[str] = Field(None, description="Category name")
    is_manual: bool = Field(False, description="Whether manually entered")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class TransactionListResponse(BaseModel):
    """Paginated transaction list response."""

    data: List[Transaction] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
