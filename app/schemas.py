from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- Shared Models ---

class Message(BaseModel):
    role: str
    content: str

# --- Request Models ---

class ChatRequest(BaseModel):
    history: List[Message]

class SelectedTextChatRequest(BaseModel):
    selected_text: str
    user_query: str

class LatestDevRequest(BaseModel):
    book_section: str

class IngestRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None

# --- Response Models ---

class HealthResponse(BaseModel):
    status: str

class ChatResponse(BaseModel):
    response: str
    reasoning: Optional[str] = None