"""Sync service for running bill synchronization as async task.

This module handles email parsing and saves transactions to local SQLite database.
"""

import asyncio
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Coroutine, List, Optional

from sqlalchemy.orm import Session

# Add parent directory to path for importing firefly_bill_sync
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from firefly_bill_sync.parsers import (
    ABCCreditCardParser,
    CCBCreditCardParser,
    CMBCreditCardParser,
)

from app.database import (
    CategoryModel,
    CategoryRuleModel,
    EmailAccountModel,
    SessionLocal,
    SyncLogModel,
    TransactionModel,
)
from app.models import SyncStatus, SyncStatusResponse


def get_last_month_start() -> str:
    """Get the first day of last month in IMAP date format."""
    from dateutil.relativedelta import relativedelta

    now = datetime.now()
    last_month = now - relativedelta(months=1)
    return datetime(last_month.year, last_month.month, 1).strftime("%d-%b-%Y")


def create_email_fetcher(email: str, password: str, imap_server: str, imap_port: int):
    """Create email fetcher with custom server settings."""
    from firefly_bill_sync.email_fetcher import EmailFetcher

    fetcher = EmailFetcher(email, password)
    fetcher.IMAP_SERVER = imap_server
    fetcher.IMAP_PORT = imap_port
    return fetcher


class SyncService:
    """Service for managing bill synchronization tasks."""

    def __init__(self):
        """Initialize sync service."""
        self.status: SyncStatus = SyncStatus.IDLE
        self.progress: int = 0
        self.started_at: Optional[datetime] = None
        self.current_account: Optional[str] = None
        self.processed_count: int = 0
        self.skipped_count: int = 0
        self.error_count: int = 0
        self.logs: List[str] = []
        self._cancel_flag: bool = False
        self._callbacks: List[Callable[[dict], Coroutine[Any, Any, None]]] = []

    def add_callback(
        self, callback: Callable[[dict], Coroutine[Any, Any, None]]
    ) -> None:
        """Add callback for progress updates (used by WebSocket)."""
        self._callbacks.append(callback)

    def remove_callback(
        self, callback: Callable[[dict], Coroutine[Any, Any, None]]
    ) -> None:
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def _notify(self, data: dict) -> None:
        """Notify all callbacks with data."""
        for callback in self._callbacks:
            try:
                await callback(data)
            except Exception:
                pass

    async def _log(self, message: str) -> None:
        """Add log message and notify callbacks."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)

        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]

        await self._notify({"type": "log", "message": log_entry})

    async def _update_progress(self, progress: int) -> None:
        """Update progress and notify callbacks."""
        self.progress = progress
        await self._notify({"type": "progress", "progress": progress})

    async def _update_status(self, status: SyncStatus) -> None:
        """Update status and notify callbacks."""
        self.status = status
        await self._notify({"type": "status", "status": status.value})

    def get_status(self) -> SyncStatusResponse:
        """Get current sync status as response model."""
        return SyncStatusResponse(
            status=self.status,
            started_at=self.started_at,
            progress=self.progress,
            current_account=self.current_account,
            processed_count=self.processed_count,
            skipped_count=self.skipped_count,
            error_count=self.error_count,
            logs=self.logs[-20:],  # Last 20 logs
        )

    def cancel(self) -> None:
        """Request cancellation of running sync."""
        self._cancel_flag = True

    def _reset(self) -> None:
        """Reset service state for new sync."""
        self.progress = 0
        self.processed_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.logs = []
        self._cancel_flag = False
        self.current_account = None

    def _generate_email_id(
        self, email_date: str, description: str, amount: float
    ) -> str:
        """Generate stable unique ID for email-parsed transaction.

        Uses normalized values to ensure consistent IDs:
        - Date: YYYY-MM-DD format (first 10 chars)
        - Description: stripped whitespace
        - Amount: absolute value with 2 decimal places
        """
        # Normalize date to YYYY-MM-DD
        normalized_date = str(email_date)[:10]
        # Normalize description
        normalized_desc = description.strip()
        # Normalize amount (2 decimal places, absolute value)
        normalized_amount = f"{abs(amount):.2f}"

        content = f"{normalized_date}|{normalized_desc}|{normalized_amount}"
        return hashlib.md5(content.encode()).hexdigest()

    def _check_duplicate(
        self, db: Session, trans_date, amount: float, description: str, source_email_id: str
    ) -> bool:
        """Check if transaction already exists using multiple criteria.

        Returns True if duplicate found.
        """
        from sqlalchemy import func

        # Method 1: Check by source_email_id (for email-imported records)
        if source_email_id:
            existing = (
                db.query(TransactionModel)
                .filter(TransactionModel.source_email_id == source_email_id)
                .first()
            )
            if existing:
                return True

        # Method 2: Check by business fields (date + amount + description)
        # This catches duplicates that may have different source_email_id
        existing = (
            db.query(TransactionModel)
            .filter(
                func.date(TransactionModel.transaction_date) == func.date(trans_date),
                func.abs(TransactionModel.amount - amount) < 0.01,
                TransactionModel.description == description.strip(),
            )
            .first()
        )
        return existing is not None

    def _match_category(self, db: Session, description: str) -> Optional[int]:
        """Match description to category using rules."""
        rules = (
            db.query(CategoryRuleModel)
            .order_by(CategoryRuleModel.priority.desc())
            .all()
        )
        for rule in rules:
            if re.search(rule.pattern, description, re.IGNORECASE):
                return rule.category_id
        return None

    def _get_parser_for_bank(self, bank_type: str):
        """Get parser instance for bank type."""
        parsers = {
            "cmb": CMBCreditCardParser(),
            "ccb": CCBCreditCardParser(),
            "abc": ABCCreditCardParser(),
        }
        return parsers.get(bank_type.lower())

    async def run_sync(
        self, since_date: Optional[str] = None, dry_run: bool = False
    ) -> None:
        """Run bill synchronization.

        Args:
            since_date: Start date for fetching emails, format "1-JAN-2025".
                       Defaults to first day of last month.
            dry_run: If True, only parse without saving to database.
        """
        self._reset()
        self.status = SyncStatus.RUNNING
        self.started_at = datetime.now()

        if since_date is None:
            since_date = get_last_month_start()

        await self._log(f"开始同步账单，起始日期: {since_date}")
        if dry_run:
            await self._log("*** 预览模式 - 不会保存到数据库 ***")

        db = SessionLocal()
        sync_log = None

        try:
            # Create sync log entry
            sync_log = SyncLogModel(
                started_at=self.started_at,
                status="running",
            )
            db.add(sync_log)
            db.commit()

            # Get active email accounts from database
            accounts = (
                db.query(EmailAccountModel)
                .filter(EmailAccountModel.is_active == 1)
                .all()
            )

            if len(accounts) == 0:
                await self._log("错误: 没有配置活跃的邮箱账户")
                await self._update_status(SyncStatus.FAILED)
                if sync_log:
                    sync_log.status = "failed"
                    sync_log.error_message = "没有配置活跃的邮箱账户"
                    sync_log.finished_at = datetime.now()
                    db.commit()
                return

            total_accounts = len(accounts)

            # Process each email account
            for account_idx, account in enumerate(accounts):
                if self._cancel_flag:
                    await self._log("同步已取消")
                    await self._update_status(SyncStatus.CANCELLED)
                    if sync_log:
                        sync_log.status = "cancelled"
                        sync_log.finished_at = datetime.now()
                        db.commit()
                    return

                self.current_account = account.email
                base_progress = int((account_idx / total_accounts) * 100)
                await self._update_progress(base_progress)
                await self._log(f"处理邮箱: {account.email} ({account.bank_type})")

                # Get parser for this bank
                parser = self._get_parser_for_bank(account.bank_type)
                if not parser:
                    await self._log(f"不支持的银行类型: {account.bank_type}")
                    self.error_count += 1
                    continue

                # Login to email
                fetcher = create_email_fetcher(
                    account.email,
                    account.password,
                    account.imap_server,
                    account.imap_port,
                )

                if not fetcher.login():
                    await self._log(f"邮箱登录失败: {account.email}")
                    self.error_count += 1
                    continue

                try:
                    subjects = parser.get_subject_keywords()
                    await self._log(f"  搜索主题: {subjects}")

                    # Fetch emails (run in thread to avoid blocking)
                    emails = await asyncio.to_thread(
                        fetcher.fetch_emails_by_subject,
                        target_subjects=subjects,
                        since_date=since_date,
                    )

                    await self._log(f"  找到 {len(emails)} 封邮件")

                    for email_idx, (html_content, email_date) in enumerate(emails):
                        if self._cancel_flag:
                            break

                        await self._log(f"  解析邮件: {email_date}")

                        # Parse email (run in thread)
                        df = await asyncio.to_thread(
                            parser.parse, html_content, email_date
                        )

                        if df.empty:
                            await self._log("    无交易记录")
                            continue

                        await self._log(f"    找到 {len(df)} 条交易")

                        # Process transactions
                        for _, row in df.iterrows():
                            if self._cancel_flag:
                                break

                            amount = row["amount"]
                            description = row["description"]
                            trans_date = row["date"]

                            # Convert date string to datetime if needed
                            if isinstance(trans_date, str):
                                from datetime import datetime as dt
                                try:
                                    trans_date = dt.strptime(trans_date, "%Y-%m-%d")
                                except ValueError:
                                    trans_date = dt.now()

                            # Generate unique ID for deduplication
                            source_email_id = self._generate_email_id(
                                str(trans_date), description, amount
                            )

                            # Check for duplicates using dual-method check
                            if self._check_duplicate(db, trans_date, amount, description, source_email_id):
                                self.skipped_count += 1
                                continue

                            # Handle refunds (negative amounts)
                            if amount < 0:
                                await self._log(
                                    f"    跳过退款: {description} | ¥{abs(amount)}"
                                )
                                continue

                            if not dry_run:
                                # Match category
                                category_id = self._match_category(db, description)

                                # Create transaction
                                transaction = TransactionModel(
                                    transaction_date=trans_date,
                                    amount=amount,
                                    description=description,
                                    category_id=category_id,
                                    transaction_type="withdrawal",
                                    source_account=account.bank_type,
                                    is_manual=0,
                                    source_email_id=source_email_id,
                                )
                                db.add(transaction)
                                self.processed_count += 1

                        if not dry_run:
                            db.commit()

                        await self._log(
                            f"    同步: {self.processed_count} 条, "
                            f"跳过重复: {self.skipped_count} 条"
                        )

                    # Update progress
                    progress = int(((account_idx + 1) / total_accounts) * 100)
                    await self._update_progress(progress)

                    # Update last sync time for account
                    account.last_sync_at = datetime.now()
                    db.commit()

                finally:
                    fetcher.logout()

            await self._update_progress(100)
            await self._log(
                f"同步完成，共处理 {self.processed_count} 条交易，"
                f"跳过 {self.skipped_count} 条重复"
            )
            await self._update_status(SyncStatus.COMPLETED)

            # Update sync log
            if sync_log:
                sync_log.status = "completed"
                sync_log.finished_at = datetime.now()
                sync_log.total_found = self.processed_count + self.skipped_count
                sync_log.total_synced = self.processed_count
                sync_log.total_skipped = self.skipped_count
                db.commit()

        except Exception as e:
            await self._log(f"同步出错: {str(e)}")
            self.error_count += 1
            await self._update_status(SyncStatus.FAILED)

            if sync_log:
                sync_log.status = "failed"
                sync_log.error_message = str(e)
                sync_log.finished_at = datetime.now()
                db.commit()

        finally:
            self.current_account = None
            db.close()
