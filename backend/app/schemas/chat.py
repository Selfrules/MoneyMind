"""Chat schemas for API requests and responses."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message."""
    id: Optional[int] = None
    role: str  # user, assistant
    content: str
    tokens_used: Optional[int] = None
    created_at: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Chat history response."""
    session_id: str
    messages: List[ChatMessage]
    total_tokens: int


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Non-streaming chat response."""
    session_id: str
    message: ChatMessage
    suggested_actions: List[str]


class SuggestedQuestion(BaseModel):
    """A suggested question for the user."""
    text: str
    category: str  # budget, spending, savings, debt, general


class SuggestedQuestionsResponse(BaseModel):
    """List of suggested questions."""
    questions: List[SuggestedQuestion]
