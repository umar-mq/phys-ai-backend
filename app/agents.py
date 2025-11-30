from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled, set_default_openai_api
from app.config import settings
from app.tools import search_coursebook, search_arxiv_papers

# --- SDK Global Configuration ---
# Disable tracing as requested (and because we might not have a platform API key)
set_tracing_disabled(True)
# Force Chat Completions API (Gemini compatibility)
set_default_openai_api("chat_completions")

# --- Client Setup ---
# Create a custom client pointing to Gemini
gemini_client = AsyncOpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url=settings.GEMINI_BASE_URL
)

# Define the model wrapper
gemini_model = OpenAIChatCompletionsModel(
    model=settings.GEMINI_MODEL,
    openai_client=gemini_client
)

# --- Agent Definitions ---

# 1. Main RAG Agent
rag_agent = Agent(
    name="Coursebook Tutor",
    instructions=(
        "You are a helpful coursebook assistant. "
        "Use the 'search_coursebook' tool to find information to answer the user's question. "
        "If the answer is not in the context, admit you don't know based on the book."
    ),
    model=gemini_model,
    tools=[search_coursebook]
)

# 2. Selected Text Context Agent
# This agent specializes in explaining specific highlighted text
context_agent = Agent(
    name="Context explainer",
    instructions=(
        "You are an expert tutor. The user has highlighted a specific section of text "
        "and asked a question about it. Explain the selected text clearly in the context "
        "of the user's query. You may use 'search_coursebook' if you need broader context."
    ),
    model=gemini_model,
    tools=[search_coursebook]
)

# 3. Latest Developments Agent
research_agent = Agent(
    name="Research Assistant",
    instructions=(
        "You are a researcher. Given a book section or topic, find the latest academic "
        "developments using the 'search_arxiv_papers' tool. Summarize the findings "
        "concisely for a student audience."
    ),
    model=gemini_model,
    tools=[search_arxiv_papers]
)