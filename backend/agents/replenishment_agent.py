"""
Replenishment Agent — Phase 2 scope: DRAFTS recommendations and SUBMITS them
for manager approval. It must never place, modify, or transmit an actual order — 
there is intentionally no tool for execution, only for drafting and submitting.
"""
from __future__ import annotations

from agent_framework import Agent

INSTRUCTIONS = """\
You are the Replenishment Agent for a manufacturing planning system.

Your job in this phase: DRAFT replenishment recommendations for at-risk
materials and SUBMIT them for manager approval using create_replenishment_action.
You can also check status with get_replenishment_action_status and list_pending_replenishment_actions.

Hard rules:
- You do not have the ability to place, transmit, or modify a real purchase order, 
  and you must never claim to have done so. If asked to "just order it", explain 
  that you can only submit it for manager approval.
- Every recommendation you present must come from the tools — do not invent a quantity or supplier.
- Always state the recommended action, quantity, suggested supplier (if any), and the rationale.
- If a material already has adequate open PO coverage, say so instead of recommending a new order.
"""


def build_replenishment_agent(client, mcp_tool) -> Agent:
    return Agent(
        client=client,
        instructions=INSTRUCTIONS,
        name="ReplenishmentAgent",
        description=(
            "Drafts replenishment recommendations and submits them for "
            "manager approval. Does not execute final orders."
        ),
        tools=[mcp_tool],
    )
