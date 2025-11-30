from fastapi import FastAPI, HTTPException
from agents import Runner
from app.schemas import (
    ChatRequest, ChatResponse, 
    SelectedTextChatRequest, 
    LatestDevRequest, 
    IngestRequest, HealthResponse
)
from app.agents import rag_agent, context_agent, research_agent
from app.vector_store import vector_store

app = FastAPI(
    title="OpenAI Agents RAG Backend",
    description="Backend for RAG Chatbot with QDrant, OpenAI Agents, and Gemini.",
    version="1.0.0"
)

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
        # Log the error in a real app
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
    
    prompt = f"""
    Previous conversation history:
    {conversation_context}
    
    Current User Question: {last_user_msg}
    """

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
    prompt = f"""
    The user is reading the following text:
    "{request.selected_text}"
    
    User Query about this text:
    "{request.user_query}"
    """
    
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
    prompt = f"Find latest developments related to this book section: {request.book_section}"
    
    try:
        result = await Runner.run(research_agent, prompt)
        return ChatResponse(response=str(result.final_output))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))