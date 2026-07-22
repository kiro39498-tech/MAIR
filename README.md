# Material Availability & Inventory Replenishment (MAIR) System

An enterprise-grade, agent-driven supply chain platform that combines a **pluggable enterprise data connector framework**, a **deterministic analytics engine**, a **Model Context Protocol (MCP) server**, a **multi-agent orchestration framework (Microsoft Agent Framework)**, and an **interactive executive dashboard** to monitor inventory health, evaluate production risks, explode complex Bills of Materials (BOM), and automate replenishment workflows with human-in-the-loop approvals.

---

## 📋 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Pluggable Data Connector Architecture](#-pluggable-data-connector-architecture)
- [Key Features](#-key-features)
- [Core Design Principles (SSOT)](#-core-design-principles-ssot)
- [Technology Stack](#-technology-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Environment Configuration](#environment-configuration)
- [API Reference](#-api-reference)
- [Multi-Agent System & MCP Layer](#-multi-agent-system--mcp-layer)
- [Replenishment Workflow State Machine](#-replenishment-workflow-state-machine)
- [Dataset & Enterprise Schema Mapping](#-dataset--enterprise-schema-mapping)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [License](#-license)

---

## 🏗 Architecture Overview

The MAIR system architecture isolates deterministic supply chain logic from LLM non-determinism and vendor-specific database contracts. Agents interact with business data **exclusively** through standardized MCP tools over stdio, while the analytics engine operates strictly on unified canonical models.

```
                  ┌─────────────────────────────────────────┐
                  │          React 19 Frontend UI           │
                  │   (TanStack Start/Router, Recharts)     │
                  └────────────────────┬────────────────────┘
                                       │ REST API calls
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           FastAPI Gateway App                            │
│                                                                          │
│   ┌───────────────────────┐             ┌────────────────────────────┐   │
│   │  Dashboard Endpoints  │             │   Replenishment Workflow   │   │
│   │ (/api/dashboard/*)    │             │   (/api/replenishment/*)   │   │
│   └───────────┬───────────┘             └─────────────┬──────────────┘   │
│               │                                       │                  │
│               │ Direct Function Call                  │ Workflows & DB   │
│               ▼                                       ▼                  │
│   ┌───────────────────────┐             ┌────────────────────────────┐   │
│   │ Deterministic Engine  │             │ SQLite DB & State Machine  │   │
│   │      (analytics/)     │             │ (Drafted → Approved)       │   │
│   └───────────▲───────────┘             └─────────────┬──────────────┘   │
│               │                                       │                  │
│               │ Master Repository Facade              │ Email Alerts     │
│               ▼                                       ▼                  │
│   ┌───────────────────────┐             ┌────────────────────────────┐   │
│   │   Domain Repositories │             │    Notification Service    │   │
│   │(Inventory, BOM, POs)  │             │    (SMTP + Token Links)    │   │
│   └───────────▲───────────┘             └────────────────────────────┘   │
│               │ Loads via ConnectorFactory                               │
│               ▼                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐   │
│   │          Pluggable Enterprise Connector Framework                 │   │
│   │  ┌───────────┐ ┌───────────────┐ ┌──────────┐ ┌───────────────┐  │   │
│   │  │ CSV/Excel │ │ SQL Server/PG │ │ SAP ERP  │ │ MS Fabric/Lake│  │   │
│   │  └───────────┘ └───────────────┘ └──────────┘ └───────────────┘  │   │
│   └──────────────────────────────────▲───────────────────────────────┘   │
│                                      │                                   │
└──────────────────────────────────────┼───────────────────────────────────┘
                                       │ REST POST /api/copilot/chat
                                       ▼
                                Azure OpenAI (gpt-4o)
```

---

## 🔌 Pluggable Data Connector Architecture

MAIR supports **20+ enterprise data sources** out of the box. The data layer is decoupled via the **Repository Pattern** and **Factory Pattern**.

```
                                  FastAPI Gateway
                                         │
                                         ▼
                            Deterministic Analytics Engine
                            (Operates on Canonical Models)
                                         │
                                         ▼
                                  Repository Layer
                   (Inventory, BOM, Supplier, Production, Purchase)
                                         │
                                         ▼
                               Connector Abstraction
                             (BaseConnector & Factory)
                                         │
      ┌─────────────────┬────────────────┼────────────────┬────────────────┐
      ▼                 ▼                ▼                ▼                ▼
 CSV / Excel       SQL Server / PG      SAP ERP         MS Fabric     REST APIs / S3
(Pandas/OpenPyXL) (SQLAlchemy/pyodbc) (RFC/OData)  (Lakehouse/SQL) (Requests/Azure)
```

### Supported Data Sources
- **Flat Files**: CSV, Excel (`.xlsx`, `.xls`), SharePoint Files, OneDrive.
- **Relational Databases**: Microsoft SQL Server (SSMS), Azure SQL, PostgreSQL, MySQL, Oracle.
- **Enterprise ERPs**: SAP S/4HANA, SAP ECC, SAP HANA.
- **Cloud Data Warehouses**: Microsoft Fabric Lakehouse, Fabric Warehouse, Fabric SQL Endpoint, Databricks, Snowflake.
- **APIs & Cloud Storage**: REST APIs, OData APIs, Amazon S3, Azure Blob Storage.

### Dynamic Switching via Configuration
Changing the underlying enterprise data source requires **zero code modifications** in analytics, MCP tools, multi-agent systems, or FastAPI endpoints. Simply update `DATA_SOURCE` in `.env`:

```ini
# Switch to Microsoft SQL Server:
DATA_SOURCE=sqlserver
SQLSERVER_CONNECTION_STRING=mssql+pyodbc://user:pass@sqlserver.corp.com/MAIR_DB?driver=ODBC+Driver+18+for+SQL+Server

# Switch to SAP S/4HANA:
DATA_SOURCE=sap
SAP_ASHOST=192.168.1.50
SAP_CLIENT=100
```

---

## ✨ Key Features

### 1. Deterministic Supply Chain Analytics Engine
- **Health Classification**: Classifies material-plant pairs into `Shortage`, `Safety Stock Warning`, `Near Reorder`, `Excess`, and `Healthy` based strictly on defined safety stock ($SS$), reorder point ($ROP$), and maximum stock ($MS$) thresholds.
- **BOM Explosion & Component Risk**: Recursively explodes multi-level Bills of Materials (BOM) to identify low-level raw material component shortages that threaten parent production orders.
- **Time-Phased Inventory Projections**: Generates 30, 60, and 90-day supply/demand projections based on open production orders and incoming purchase order schedules.
- **Multi-Criteria Priority Scoring**: Ranks at-risk materials using financial impact, production dependency counts, lead times, and current stock severity.

### 2. Schema Mapping & Data Quality Validation Engine
- **Configurable Schema Mapping**: Converts enterprise column headers (e.g., SAP `MATNR`, `WERKS`, `LABST` or Custom `MaterialCode`) into canonical fields using JSON mapping files (`mappings/sap.json`, `mappings/fabric.json`, `mappings/sqlserver.json`).
- **Validation Engine**: Performs schema compliance checks, flags missing required fields, detects null primary keys, flags duplicate primary keys, handles invalid date formats, and logs negative inventory warnings.
- **High Performance & Caching**: Repository caching, lazy loading, and streaming generators support datasets exceeding **1,000,000+ inventory records**.

### 3. Multi-Agent AI Copilot & MCP Tools
- **Built on Microsoft Agent Framework**: Utilizes specialized LLM agents powered by Azure OpenAI (`gpt-4o`).
- **Inventory Intelligence Agent**: Specializes in stock status, safety thresholds, and health diagnostic queries.
- **Production Impact Agent**: Analyzes BOM dependencies, affected production orders, and finished goods at risk.
- **Replenishment Agent**: Formulates purchase recommendations, Economic Order Quantity (EOQ) calculations, and supplier allocations.
- **Strict Model Context Protocol (MCP)**: Agents access analytics data solely via an MCP server connected over stdio stream.

### 4. Enterprise Replenishment Workflow & Governance
- **State Machine Transitions**: Enforces rigid status flow: `Drafted` $\rightarrow$ `PendingApproval` $\rightarrow$ `Approved` / `Rejected` $\rightarrow$ `Executed` / `Failed`.
- **Deduplication & Audit Trail**: Prevents redundant actions for the same material-plant key and maintains timestamped notes for state changes.
- **One-Click Tokenized Email Approvals**: Generates unique secure tokens and emails actionable links directly to supply chain managers.
- **Mock ERP Execution Connector**: Simulates purchase order creation safely in `purchase_orders_created.csv` without corrupting baseline seed data.

---

## 🎯 Core Design Principles (SSOT)

1. **Deterministic Calculations are the Single Source of Truth**:
   All stock status classifications, reorder points, component quantities, and priority scores originate strictly from pure Python functions in `analytics/`. **AI agents never guess or calculate inventory values.**
2. **Strict Data Source Agnosticism**:
   The analytics engine receives only canonical models from the repository layer. It never knows whether data came from SAP, SQL Server, Fabric, or CSV files.
3. **Strict MCP Data Isolation**:
   No agent code directly imports database repositories or data models. Agents query data exclusively through tools declared in `mcp_server/server.py`.
4. **Draft-First Decoupled Execution**:
   AI agents and automated triggers generate **draft actions**. Execution is decoupled behind a REST endpoint requiring explicit authorization.

---

## 🛠 Technology Stack

### Backend
| Technology | Role |
| :--- | :--- |
| **Python 3.11+** | Core programming language |
| **FastAPI** | REST API gateway & route handlers |
| **Uvicorn** | ASGI web server |
| **Microsoft Agent Framework** | Multi-agent creation & orchestration |
| **Model Context Protocol (MCP)** | Tool standardization interface |
| **SQLAlchemy / SQLite** | Persistence layer & workflow state tracking |
| **Pandas / NumPy / PyODBC** | Connector loading & vectorized data processing |
| **Pytest** | Automated unit & integration testing (50 tests) |

### Frontend
| Technology | Role |
| :--- | :--- |
| **React 19** | UI framework |
| **TanStack Start / Router** | Full-stack SSR framework & type-safe routing |
| **TanStack Query** | Server state management & caching |
| **TailwindCSS** | Utility-first styling engine |
| **Radix UI** | Accessible component primitives |
| **Recharts** | Interactive supply chain data visualization |
| **Lucide React** | Modern iconography |

---

## 📁 Repository Structure

```
MAIR/
├── README.md                           # Master project documentation
├── backend/                            # FastAPI, MCP, Multi-Agent & Analytics
│   ├── README.md                       # Backend-specific architecture guide
│   ├── .env.example                    # Environment variables template
│   ├── requirements.txt                # Python dependencies
│   ├── main.py / smoke_test.py         # Entry points and smoke test scripts
│   ├── agents/                         # Agent definitions & orchestrator
│   ├── analytics/                      # Pure deterministic engine functions
│   ├── api/                            # FastAPI router & endpoints
│   ├── config/                         # Central settings & env configuration
│   ├── connectors/                     # Pluggable Enterprise Connector Framework
│   │   ├── base.py                     # BaseConnector ABC
│   │   ├── registry.py                 # Connector Registry
│   │   ├── connector_factory.py        # Connector Factory
│   │   ├── mapping_engine.py           # Enterprise column mapping engine
│   │   ├── validation_engine.py        # Data quality validator
│   │   ├── caching.py                  # High-performance caching & streaming
│   │   ├── csv_connector.py            # CSV connector
│   │   ├── excel_connector.py          # Excel connector
│   │   ├── sqlserver_connector.py      # SQL Server / Azure SQL connector
│   │   ├── postgres_connector.py       # PostgreSQL connector
│   │   ├── mysql_connector.py          # MySQL connector
│   │   ├── oracle_connector.py         # Oracle connector
│   │   ├── fabric_connector.py         # MS Fabric Lakehouse/Warehouse connector
│   │   ├── sap_connector.py            # SAP S/4HANA & ECC connector
│   │   ├── hana_connector.py           # SAP HANA database connector
│   │   ├── rest_connector.py           # REST / OData API connector
│   │   ├── blob_connector.py           # Cloud Object Storage (S3 / Azure Blob)
│   │   └── sharepoint_connector.py     # SharePoint & OneDrive connector
│   ├── mappings/                       # Enterprise JSON column mappings
│   ├── models/                         # Canonical models (canonical.py & schemas.py)
│   ├── persistence/                    # SQLAlchemy database models & state machine
│   ├── repositories/                   # Domain Repositories (Inventory, BOM, POs, etc.)
│   ├── services/                       # Workflow state machine & notification engine
│   ├── docs/                           # Documentation & MIGRATION_GUIDE.md
│   └── tests/                          # Pytest suite (50 tests passing)
├── frontend/                           # React 19 + TanStack web dashboard
└── data/                               # Dataset & CSV baseline files
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: Version 3.11 or higher
- **Node.js**: Version 18.0 or higher (or `bun`)
- **Azure OpenAI Service**: Access key and endpoint (required for AI Copilot agent features)

---

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Copy `.env.example` to `.env` and configure credentials:
   ```bash
   cp .env.example .env
   ```

5. **Start the FastAPI server**:
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```
   The API server will run at `http://localhost:8000`.

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node modules**:
   ```bash
   npm install
   # or using bun:
   bun install
   ```

3. **Launch the development server**:
   ```bash
   npm run dev
   # or using bun:
   bun dev
   ```
   The web dashboard will be accessible at `http://localhost:5173`.

---

## 📡 API Reference

### Dashboard Endpoints (`/api/dashboard`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/dashboard/summary` | Get aggregated inventory health counts across all material-plant keys |
| `GET` | `/api/dashboard/materials` | Query materials with optional `status`, `plant_id`, or `search` parameters |
| `GET` | `/api/dashboard/materials/{material_id}/{plant_id}` | Retrieve comprehensive detail for a material (health, BOM, projections, PO coverage) |
| `GET` | `/api/dashboard/priority` | Get top-N prioritized at-risk materials sorted by criticality score |
| `GET` | `/api/dashboard/recommendations` | Generate draft replenishment recommendations for all shortage/warning items |

### Replenishment Workflow Endpoints (`/api/replenishment`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/replenishment/run` | Trigger automated workflow (identifies shortages, drafts actions, sends emails) |
| `GET` | `/api/replenishment/actions` | Retrieve all tracked replenishment actions and their state machine statuses |
| `GET` | `/api/replenishment/actions/{action_id}/approve` | Tokenized endpoint to approve an action (`?token=<uuid>`) |
| `GET` | `/api/replenishment/actions/{action_id}/reject` | Tokenized endpoint to reject an action (`?token=<uuid>`) |
| `POST` | `/api/replenishment/actions/{action_id}/execute` | Execute an approved action (creates entry in `purchase_orders_created.csv`) |

### AI Copilot Endpoint (`/api/copilot`)

| Method | Endpoint | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/copilot/chat` | `{"message": "What materials are in critical shortage at Plant P001?"}` | Sends user prompt through orchestrator to specialist agents via MCP tools |

---

## 🧪 Testing & Quality Assurance

Run the pytest suite to validate deterministic calculations, enterprise connectors, schema mapping, data validation, and workflow state machine transitions:

```bash
cd backend
.\.venv\Scripts\pytest tests/ -v
```

All 50 unit and integration tests execute successfully in under 25 seconds.

---

## 📄 License

This project is released under the **MIT License**.
