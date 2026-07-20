# Material Availability & Inventory Replenishment Agent — Backend

Deterministic analytics engine + MCP layer + 3-agent system (Microsoft Agent
Framework) + FastAPI, built against the generated dataset (`data/csv/`).

## Scope of this codebase (Phase 1 & Phase 2)

- Full deterministic analytics engine (health classification, BOM explosion,
  time-phased projection, PO coverage, production impact, priority scoring,
  replenishment recommendations).
- MCP server exposing every analytics function as a tool.
- Three agents (Inventory Intelligence, Production Impact, Replenishment) +
  an orchestrator, built on `agent-framework` with real `MCPStdioTool`
  connections to the MCP server.
- FastAPI: read-only dashboard endpoints (call analytics directly) + one
  `/api/copilot/chat` endpoint (goes through the orchestrator/agents).

**Phase 2 additions**:
- Persistence layer with SQLite and SQLAlchemy.
- Workflow state machine enforcing strict transitions (Drafted -> PendingApproval -> Approved/Rejected -> Executed/Failed) and maintaining an audit trail.
- Notification service supporting automated email approvals.
- Mock execution connector that tracks fulfilled purchase orders safely in a separate CSV file without mutating the dataset.
- New endpoints for executing actions, confirming approvals via email tokens, and processing at-risk materials.
- *Critical Note on Email*: No email is sent from automated tests. The first live send should be triggered manually via `POST /api/replenishment/run` against real SMTP credentials to confirm delivery before relying on it.

## Folder structure

```
config/          Settings (env-driven)
models/          Canonical Pydantic data model (SSOT section 7)
connectors/      Data source connectors (csv_connector.py is Phase 1's only one)
data/            Dataset CSVs + in-memory repository (loads via the active connector)
analytics/       Deterministic engine — the only place calculations happen
mcp_server/      MCP server wrapping analytics as tools
agents/          3 agents + orchestrator (agent-framework, Azure OpenAI)
api/             FastAPI app + routes
tests/           pytest suite, validated against data/csv/_answer_key_inventory_status.csv
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Azure OpenAI values if you want the copilot route
```

## Run the tests (no Azure OpenAI needed)

```bash
pytest tests/ -v
```
14 tests, including a check that health classification agrees with the
dataset's ground-truth answer key (currently 100% on the shipped dataset).

## Run the MCP server standalone (no Azure OpenAI needed)

```bash
python -m mcp_server.server
```
Speaks MCP over stdio. Useful for testing tools directly with any MCP client
before wiring up agents.

## Run the API (dashboard works without Azure OpenAI; copilot needs it)

```bash
uvicorn api.main:app --reload
```
- `GET /api/dashboard/summary` — status counts across all materials
- `GET /api/dashboard/materials?status=Shortage` — filtered material list
- `GET /api/dashboard/materials/{material_id}/{plant_id}` — full detail
  (health + production impact + projection + PO coverage)
- `GET /api/dashboard/priority` — top-N at-risk materials, ranked
- `GET /api/dashboard/recommendations` — draft replenishment recommendations
- `POST /api/copilot/chat {"message": "..."}` — orchestrator + 3 agents
  (requires `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_API_KEY` in `.env`)
- `POST /api/replenishment/run` — process at-risk materials (drafts, submits, notifies)
- `GET /api/replenishment/actions` — list all actions
- `GET /api/replenishment/actions/{action_id}/approve?token=...` — approve action via token
- `POST /api/replenishment/actions/{action_id}/execute` — execute an approved action

## Design principles this code follows (from the SSOT)

1. **Deterministic calculations are the only source of truth.** Every number
   an agent or API response returns traces back to a function in
   `analytics/`, never to an LLM guess.
2. **Agents only reach data through MCP.** No agent file imports
   `data.repository` or `analytics.*` directly — only `mcp_server/server.py`
   does, and agents call it exclusively via `MCPStdioTool`.
3. **The connector is swappable.** `connectors/csv_connector.py` is the only
   thing that knows about CSV files. A future SAP/SQL/Fabric connector
   implements `connectors/base_connector.py` and nothing above it changes.
4. **Draft, don't act.** The agent doesn't write to external systems directly. The execution layer is completely decoupled and inaccessible by the AI, requiring an explicit REST call.

## Known limitations to fix

- `agents/orchestrator.py` spawns its own MCP subprocess per orchestrator
  instance — fine for one API process, but revisit if you scale to multiple
  workers (share one MCP server over `MCPStreamableHTTPTool` instead).
- No auth on the API yet — add before this touches anything but localhost. Note that approval is currently link-based with no login/auth on the approve/reject endpoints — anyone with the link can approve, which is acceptable for a single-user local setup but must change before this goes anywhere multi-user.
- Execution is currently a mock CSV write (`purchase_orders_created.csv`), not a real ERP API call.
- `analytics/projection.py` only looks at production-order demand, not
  `demand_forecast.csv` — wire in forecast-driven demand if you want
  projections to extend meaningfully past the current open production orders.
