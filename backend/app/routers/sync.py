"""Sync control API router."""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Add parent directory to path for importing firefly_bill_sync
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.models import SyncStartRequest, SyncStatus, SyncStatusResponse
from app.services.sync_service import SyncService

router = APIRouter()

# Global sync service instance
sync_service = SyncService()


@router.post("/start", response_model=SyncStatusResponse)
async def start_sync(request: SyncStartRequest) -> SyncStatusResponse:
    """Start a new sync task.

    If a sync is already running, returns the current status.
    """
    if sync_service.status == SyncStatus.RUNNING:
        return sync_service.get_status()

    # Start sync in background
    asyncio.create_task(
        sync_service.run_sync(
            since_date=request.since_date,
            dry_run=request.dry_run,
        )
    )

    # Wait a moment for sync to start
    await asyncio.sleep(0.1)
    return sync_service.get_status()


@router.get("/status", response_model=SyncStatusResponse)
async def get_status() -> SyncStatusResponse:
    """Get current sync status."""
    return sync_service.get_status()


@router.post("/cancel")
async def cancel_sync() -> dict:
    """Cancel the running sync task."""
    if sync_service.status != SyncStatus.RUNNING:
        return {"message": "No sync task is running", "cancelled": False}

    sync_service.cancel()
    return {"message": "Sync task cancelled", "cancelled": True}


@router.websocket("/ws")
async def sync_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time sync progress updates.

    Sends JSON messages with format:
    {
        "type": "log" | "progress" | "status",
        "message": "...",
        "progress": 0-100,
        "status": "idle" | "running" | "completed" | "failed" | "cancelled"
    }
    """
    await websocket.accept()

    # Register callback for updates
    async def send_update(data: dict):
        try:
            await websocket.send_json(data)
        except Exception:
            pass

    sync_service.add_callback(send_update)

    try:
        # Send initial status
        await websocket.send_json(
            {
                "type": "status",
                "status": sync_service.status.value,
                "progress": sync_service.progress,
            }
        )

        # Keep connection alive and wait for messages
        while True:
            try:
                # Wait for any client message (keepalive)
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        pass
    finally:
        sync_service.remove_callback(send_update)
