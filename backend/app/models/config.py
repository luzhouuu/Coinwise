"""Configuration data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EmailAccount(BaseModel):
    """Email account information (password masked)."""

    id: int = Field(..., description="Account ID")
    email: str = Field(..., description="Email address")
    imap_server: str = Field(..., description="IMAP server address")
    imap_port: int = Field(993, description="IMAP port")
    bank_type: str = Field(..., description="Bank type: cmb/ccb/abc")
    is_active: bool = Field(True, description="Whether account is active")
    last_sync_at: Optional[datetime] = Field(None, description="Last sync time")

    class Config:
        """Pydantic config."""

        from_attributes = True


class EmailAccountCreate(BaseModel):
    """Request body for creating email account."""

    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=1, description="IMAP password or app token")
    imap_server: str = Field(..., description="IMAP server address")
    imap_port: int = Field(993, description="IMAP port")
    bank_type: str = Field(..., description="Bank type: cmb/ccb/abc")


class EmailAccountUpdate(BaseModel):
    """Request body for updating email account."""

    email: Optional[str] = Field(None, description="Email address")
    password: Optional[str] = Field(None, description="IMAP password or app token")
    imap_server: Optional[str] = Field(None, description="IMAP server address")
    imap_port: Optional[int] = Field(None, description="IMAP port")
    bank_type: Optional[str] = Field(None, description="Bank type")
    is_active: Optional[bool] = Field(None, description="Whether account is active")


class Category(BaseModel):
    """Category information."""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    icon: Optional[str] = Field(None, description="Icon name")
    color: Optional[str] = Field(None, description="Color hex code")
    parent_id: Optional[int] = Field(None, description="Parent category ID")

    class Config:
        """Pydantic config."""

        from_attributes = True


class CategoryCreate(BaseModel):
    """Request body for creating category."""

    name: str = Field(..., description="Category name")
    icon: Optional[str] = Field(None, description="Icon name")
    color: Optional[str] = Field(None, description="Color hex code")
    parent_id: Optional[int] = Field(None, description="Parent category ID")


class CategoryRule(BaseModel):
    """Category rule for auto-categorization."""

    id: int = Field(..., description="Rule ID")
    pattern: str = Field(..., description="Matching pattern")
    category_id: int = Field(..., description="Target category ID")
    category_name: Optional[str] = Field(None, description="Category name")
    priority: int = Field(0, description="Rule priority")

    class Config:
        """Pydantic config."""

        from_attributes = True


class CategoryRuleCreate(BaseModel):
    """Request body for creating category rule."""

    pattern: str = Field(..., description="Matching pattern")
    category_id: int = Field(..., description="Target category ID")
    priority: int = Field(0, description="Rule priority")


class CategoryRulesResponse(BaseModel):
    """Response containing all category rules."""

    rules: List[CategoryRule] = Field(..., description="List of category rules")


class CategoryRuleUpdate(BaseModel):
    """Request body for updating category rule."""

    pattern: Optional[str] = Field(None, description="Matching pattern")
    category_id: Optional[int] = Field(None, description="Target category ID")
    priority: Optional[int] = Field(None, description="Rule priority")


class BlacklistRule(BaseModel):
    """交易黑名单规则"""

    id: int = Field(..., description="Rule ID")
    pattern: str = Field(..., description="匹配模式（交易描述中包含此字符串则排除）")
    reason: Optional[str] = Field(None, description="排除原因说明")
    is_active: bool = Field(True, description="是否启用")

    class Config:
        """Pydantic config."""

        from_attributes = True


class BlacklistRuleCreate(BaseModel):
    """Request body for creating blacklist rule."""

    pattern: str = Field(..., min_length=1, description="匹配模式")
    reason: Optional[str] = Field(None, description="排除原因说明")


class BlacklistRulesResponse(BaseModel):
    """Response containing all blacklist rules."""

    rules: List[BlacklistRule] = Field(..., description="黑名单规则列表")
