"""Chat router for bill assistant."""
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    reply: str
    success: bool = True


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Send a message to the chat assistant and get a response."""
    chat_service = ChatService(db)

    # Convert history to dict format
    history = None
    if request.history:
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]

    # Get response from Gemini with Function Calling
    reply = await chat_service.chat(request.message, history)

    return ChatResponse(reply=reply, success=True)


@router.get("/categories")
async def get_available_categories(
    db: Session = Depends(get_db),
):
    """Get available categories for chat reference."""
    chat_service = ChatService(db)
    return chat_service.get_all_categories()
