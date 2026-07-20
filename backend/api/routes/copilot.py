"""
AI copilot endpoint — the one route in this backend that goes through the
agent/orchestrator layer instead of calling analytics directly. Requires
AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY to be set.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from collections import deque

router = APIRouter(prefix="/api/copilot", tags=["copilot"])

_orchestrator = None
# Global memory queue to store last 5 conversation turns
chat_memory = deque(maxlen=5)


def _get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from agents.orchestrator import MaterialPlanningOrchestrator
        _orchestrator = MaterialPlanningOrchestrator()
    return _orchestrator


async def _reformulate_query(history: list, current_message: str) -> str:
    from agent_framework import Agent
    from agents.client_factory import get_azure_openai_client
    
    prompt = (
        "Given the following conversation history and a new user question, formulate a standalone "
        "question that captures the user's intent. If the new question is completely unrelated to "
        "the history, just return the new question unchanged. Do not add any conversational filler, "
        "just output the reformulated question.\n\nHistory:\n"
    )
    for m in history:
        prompt += f"User: {m['user']}\nAssistant: {m['assistant']}\n"
    prompt += f"\nNew Question: {current_message}\n\nReformulated Question:"
    
    client = get_azure_openai_client()
    reformulator = Agent(
        client=client,
        instructions="You are a query reformulator. Output ONLY the standalone reformulated query, without any prefixes, quotes, or conversational filler.",
        name="Reformulator"
    )
    result = await reformulator.run(prompt)
    return str(result).strip()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        orchestrator = _get_orchestrator()
    except RuntimeError as e:
        raise HTTPException(503, str(e))
        
    query_to_run = req.message
    
    if len(chat_memory) > 0:
        try:
            query_to_run = await _reformulate_query(list(chat_memory), req.message)
        except Exception:
            # Fallback to the original message if reformulation fails (e.g. rate limit, config missing)
            query_to_run = req.message

    reply = await orchestrator.ask(query_to_run)
    
    chat_memory.append({"user": query_to_run, "assistant": reply})
    
    return ChatResponse(reply=reply)
