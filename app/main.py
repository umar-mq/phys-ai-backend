from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents import Runner

# Import Config, DB, and Routers
from app.config import settings
from app.database import init_db
from app.routers import auth
from app.schemas import (
    ChatRequest, ChatResponse, 
    SelectedTextChatRequest, 
    LatestDevRequest, 
    IngestRequest, HealthResponse
)
from app.agents import rag_agent, context_agent, research_agent
from app.vector_store import vector_store
from app.prompts import (
    RAG_USER_TEMPLATE,
    CONTEXT_USER_TEMPLATE,
    RESEARCH_USER_TEMPLATE
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB Tables on startup
    init_db()
    yield

app = FastAPI(
    title="OpenAI Agents RAG Backend",
    description="Backend for RAG Chatbot with QDrant, OpenAI Agents, Neon, and Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Configuration ---
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---
app.include_router(auth.router)

# --- Existing Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok"}

@app.post("/api/ingest")
async def ingest_endpoint(request: IngestRequest):
    """
    Ingest Endpoint: Receives text and optional metadata to store in the Vector DB.
    """
    try:
        await vector_store.ingest_text(request.text, request.metadata)
        return {
            "status": "success", 
            "message": "Text processed and stored in QDrant successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Standard RAG Chat Pipeline.
    """
    if not request.history:
        raise HTTPException(status_code=400, detail="History cannot be empty")

    last_user_msg = request.history[-1].content
    conversation_context = "\n".join([f"{msg.role}: {msg.content}" for msg in request.history[:-1]])
    
    prompt = RAG_USER_TEMPLATE.format(
        history=conversation_context,
        last_user_msg=last_user_msg
    )

    try:
        result = await Runner.run(rag_agent, prompt)
        return ChatResponse(response=str(result.final_output))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/selected", response_model=ChatResponse)
async def selected_chat_endpoint(request: SelectedTextChatRequest):
    """
    RAG Selection Pipeline: Contextualizes a query based on selected text.
    """
    prompt = CONTEXT_USER_TEMPLATE.format(
        selected_text=request.selected_text,
        user_query=request.user_query
    )
    
    try:
        result = await Runner.run(context_agent, prompt)
        return ChatResponse(response=str(result.final_output))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/latest-developments", response_model=ChatResponse)
async def latest_developments_endpoint(request: LatestDevRequest):
    """
    Latest Development Pipeline: Checks Arxiv for updates on a topic.
    """
    prompt = RESEARCH_USER_TEMPLATE.format(
        book_section=request.book_section
    )
    
    try:
        result = await Runner.run(research_agent, prompt)
        return ChatResponse(response=str(result.final_output))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))