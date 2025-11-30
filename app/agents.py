from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled, set_default_openai_api
from app.config import settings
from app.tools import search_coursebook, search_arxiv_papers
from app.prompts import (
    RAG_SYSTEM_INSTRUCTION,
    CONTEXT_SYSTEM_INSTRUCTION,
    RESEARCH_SYSTEM_INSTRUCTION
)

# --- SDK Global Configuration ---
set_tracing_disabled(True)
set_default_openai_api("chat_completions")

# --- Client Setup ---
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
    instructions=RAG_SYSTEM_INSTRUCTION,
    model=gemini_model,
    tools=[search_coursebook]
)

# 2. Selected Text Context Agent
context_agent = Agent(
    name="Context explainer",
    instructions=CONTEXT_SYSTEM_INSTRUCTION,
    model=gemini_model,
    tools=[search_coursebook]
)

# 3. Latest Developments Agent
research_agent = Agent(
    name="Research Assistant",
    instructions=RESEARCH_SYSTEM_INSTRUCTION,
    model=gemini_model,
    tools=[search_arxiv_papers]
)