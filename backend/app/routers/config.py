"""Configuration management API router."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import (
    CategoryModel,
    CategoryRuleModel,
    EmailAccountModel,
    get_db,
    init_default_categories,
)
from app.models import (
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

router = APIRouter()


# Email Accounts
@router.get("/email-accounts", response_model=List[EmailAccount])
async def list_email_accounts(
    db: Session = Depends(get_db),
) -> List[EmailAccount]:
    """Get all configured email accounts (passwords masked)."""
    accounts = db.query(EmailAccountModel).all()
    return [
        EmailAccount(
            id=a.id,
            email=a.email,
            imap_server=a.imap_server,
            imap_port=a.imap_port,
            bank_type=a.bank_type,
            is_active=bool(a.is_active),
            last_sync_at=a.last_sync_at,
        )
        for a in accounts
    ]


@router.post("/email-accounts", response_model=EmailAccount, status_code=201)
async def create_email_account(
    data: EmailAccountCreate,
    db: Session = Depends(get_db),
) -> EmailAccount:
    """Add a new email account."""
    # Check if email already exists
    existing = db.query(EmailAccountModel).filter(
        EmailAccountModel.email == data.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email account already exists")

    account = EmailAccountModel(
        email=data.email,
        password=data.password,
        imap_server=data.imap_server,
        imap_port=data.imap_port,
        bank_type=data.bank_type,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    return EmailAccount(
        id=account.id,
        email=account.email,
        imap_server=account.imap_server,
        imap_port=account.imap_port,
        bank_type=account.bank_type,
        is_active=bool(account.is_active),
        last_sync_at=account.last_sync_at,
    )


@router.put("/email-accounts/{account_id}", response_model=EmailAccount)
async def update_email_account(
    account_id: int,
    data: EmailAccountUpdate,
    db: Session = Depends(get_db),
) -> EmailAccount:
    """Update an email account."""
    account = db.query(EmailAccountModel).filter(
        EmailAccountModel.id == account_id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)

    return EmailAccount(
        id=account.id,
        email=account.email,
        imap_server=account.imap_server,
        imap_port=account.imap_port,
        bank_type=account.bank_type,
        is_active=bool(account.is_active),
        last_sync_at=account.last_sync_at,
    )


@router.delete("/email-accounts/{account_id}")
async def delete_email_account(
    account_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Delete an email account."""
    account = db.query(EmailAccountModel).filter(
        EmailAccountModel.id == account_id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")

    email = account.email
    db.delete(account)
    db.commit()
    return {"message": "Account deleted", "email": email}


# Categories
@router.get("/categories", response_model=List[Category])
async def list_categories(
    db: Session = Depends(get_db),
) -> List[Category]:
    """Get all categories."""
    # Initialize default categories if empty
    init_default_categories(db)

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


@router.post("/categories", response_model=Category, status_code=201)
async def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
) -> Category:
    """Create a new category."""
    existing = db.query(CategoryModel).filter(
        CategoryModel.name == data.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = CategoryModel(
        name=data.name,
        icon=data.icon,
        color=data.color,
        parent_id=data.parent_id,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return Category(
        id=category.id,
        name=category.name,
        icon=category.icon,
        color=category.color,
        parent_id=category.parent_id,
    )


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Delete a category."""
    category = db.query(CategoryModel).filter(
        CategoryModel.id == category_id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    name = category.name
    db.delete(category)
    db.commit()
    return {"message": "Category deleted", "name": name}


# Category Rules
@router.get("/category-rules", response_model=CategoryRulesResponse)
async def get_category_rules(
    db: Session = Depends(get_db),
) -> CategoryRulesResponse:
    """Get all category rules."""
    rules = db.query(CategoryRuleModel).order_by(CategoryRuleModel.priority.desc()).all()
    return CategoryRulesResponse(
        rules=[
            CategoryRule(
                id=r.id,
                pattern=r.pattern,
                category_id=r.category_id,
                category_name=r.category.name if r.category else None,
                priority=r.priority,
            )
            for r in rules
        ]
    )


@router.post("/category-rules", response_model=CategoryRule, status_code=201)
async def create_category_rule(
    data: CategoryRuleCreate,
    db: Session = Depends(get_db),
) -> CategoryRule:
    """Create a new category rule."""
    # Verify category exists
    category = db.query(CategoryModel).filter(
        CategoryModel.id == data.category_id
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    rule = CategoryRuleModel(
        pattern=data.pattern,
        category_id=data.category_id,
        priority=data.priority,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    return CategoryRule(
        id=rule.id,
        pattern=rule.pattern,
        category_id=rule.category_id,
        category_name=category.name,
        priority=rule.priority,
    )


@router.put("/category-rules/{rule_id}", response_model=CategoryRule)
async def update_category_rule(
    rule_id: int,
    data: CategoryRuleUpdate,
    db: Session = Depends(get_db),
) -> CategoryRule:
    """Update a category rule."""
    rule = db.query(CategoryRuleModel).filter(
        CategoryRuleModel.id == rule_id
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)

    return CategoryRule(
        id=rule.id,
        pattern=rule.pattern,
        category_id=rule.category_id,
        category_name=rule.category.name if rule.category else None,
        priority=rule.priority,
    )


@router.delete("/category-rules/{rule_id}")
async def delete_category_rule(
    rule_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Delete a category rule."""
    rule = db.query(CategoryRuleModel).filter(
        CategoryRuleModel.id == rule_id
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted", "id": rule_id}
