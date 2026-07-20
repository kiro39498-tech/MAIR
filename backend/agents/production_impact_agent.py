"""
Production Impact Agent — read-only. Translates a material constraint into
its effect on production: which orders are threatened, how much quantity is
at risk, and how urgent that is. Used by the Replenishment Agent (and the
copilot) to prioritize.
"""
from __future__ import annotations

from agent_framework import Agent

INSTRUCTIONS = """\
You are the Production Impact Agent for a manufacturing planning system.

Your job: given a material and plant, determine which production orders are
threatened and how severe the impact is, using get_production_impact and
get_products_using_material.

Rules you must follow:
- Never invent which products or orders are affected — always retrieve
  this via tool calls against the BOM and production order data.
- Explain severity in business terms: how many orders, how much quantity,
  and the earliest due date at risk.
- You do not recommend replenishment actions yourself — you report impact
  so the Replenishment Agent (or the orchestrator) can weigh it.
"""


def build_production_impact_agent(client, mcp_tool) -> Agent:
    return Agent(
        client=client,
        instructions=INSTRUCTIONS,
        name="ProductionImpactAgent",
        description=(
            "Maps material shortages to the production orders and quantity "
            "they threaten, via the BOM."
        ),
        tools=[mcp_tool],
    )
