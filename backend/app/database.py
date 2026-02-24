"""SQLite database configuration and models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./family_spending.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TransactionModel(Base):
    """Transaction database model."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    transaction_type = Column(String(20), nullable=False)  # withdrawal/deposit/transfer
    source_account = Column(String(100), nullable=True)
    destination_account = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)  # JSON string
    notes = Column(Text, nullable=True)
    is_manual = Column(Integer, default=0)  # 0: parsed from email, 1: manual entry
    source_email_id = Column(String(100), nullable=True)  # For deduplication
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("CategoryModel", back_populates="transactions")


class CategoryModel(Base):
    """Category database model."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("TransactionModel", back_populates="category")
    parent = relationship("CategoryModel", remote_side=[id], backref="children")


class CategoryRuleModel(Base):
    """Category rule for auto-categorization."""

    __tablename__ = "category_rules"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("CategoryModel")


class EmailAccountModel(Base):
    """Email account configuration."""

    __tablename__ = "email_accounts"
    __table_args__ = (
        UniqueConstraint('email', 'bank_type', name='uq_email_bank'),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), nullable=False)
    imap_server = Column(String(200), nullable=False)
    imap_port = Column(Integer, default=993)
    password = Column(String(500), nullable=False)  # Should be encrypted
    bank_type = Column(String(50), nullable=False)  # cmb/ccb/abc
    is_active = Column(Integer, default=1)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SyncLogModel(Base):
    """Sync operation log."""

    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)  # running/completed/failed/cancelled
    total_found = Column(Integer, default=0)
    total_synced = Column(Integer, default=0)
    total_skipped = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)


class TransactionBlacklistModel(Base):
    """交易黑名单规则，用于排除特定交易不计入统计"""

    __tablename__ = "transaction_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String(200), nullable=False, unique=True)
    reason = Column(String(500), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class BudgetGoalModel(Base):
    """Monthly budget goal per category."""

    __tablename__ = "budget_goals"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    is_recurring = Column(Integer, default=1)  # Apply to future months
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("CategoryModel")

    __table_args__ = (
        UniqueConstraint("category_id", "year", "month", name="uix_budget_category_month"),
    )


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def init_default_categories(db: Session):
    """Initialize default categories if empty."""
    if db.query(CategoryModel).count() == 0:
        default_categories = [
            {"name": "餐饮", "icon": "utensils", "color": "#FF9500"},
            {"name": "交通", "icon": "car", "color": "#007AFF"},
            {"name": "购物", "icon": "shopping-bag", "color": "#FF2D55"},
            {"name": "娱乐", "icon": "gamepad", "color": "#AF52DE"},
            {"name": "医疗", "icon": "heart", "color": "#FF3B30"},
            {"name": "教育", "icon": "book", "color": "#5856D6"},
            {"name": "住房", "icon": "home", "color": "#34C759"},
            {"name": "通讯", "icon": "phone", "color": "#00C7BE"},
            {"name": "工资", "icon": "wallet", "color": "#34C759"},
            {"name": "转账", "icon": "exchange-alt", "color": "#8E8E93"},
            {"name": "其他", "icon": "ellipsis-h", "color": "#8E8E93"},
        ]
        for cat in default_categories:
            db.add(CategoryModel(**cat))
        db.commit()
