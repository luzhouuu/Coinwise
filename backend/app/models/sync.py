"""Sync task data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SyncStatus(str, Enum):
    """Sync task status enumeration."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SyncStartRequest(BaseModel):
    """Request body for starting a sync task."""

    since_date: Optional[str] = Field(
        None,
        description="Start date for sync, format: '1-JAN-2025'. Defaults to last month.",
        examples=["1-DEC-2024"],
    )
    dry_run: bool = Field(
        False,
        description="If true, only parse without submitting to Firefly III",
    )


class SyncStatusResponse(BaseModel):
    """Response for sync status query."""

    status: SyncStatus = Field(..., description="Current sync status")
    started_at: Optional[datetime] = Field(None, description="Sync start time")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage 0-100")
    current_account: Optional[str] = Field(
        None, description="Currently processing email account"
    )
    processed_count: int = Field(0, description="Number of transactions processed")
    skipped_count: int = Field(0, description="Number of duplicates skipped")
    error_count: int = Field(0, description="Number of errors encountered")
    logs: List[str] = Field(default_factory=list, description="Recent log messages")


class SyncLogMessage(BaseModel):
    """WebSocket message for sync log updates."""

    type: str = Field(..., description="Message type: log/progress/status")
    message: Optional[str] = Field(None, description="Log message content")
    progress: Optional[int] = Field(None, description="Progress percentage")
    status: Optional[SyncStatus] = Field(None, description="Status update")
