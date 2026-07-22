# MAIR Backend — Pluggable Enterprise Data Connectors & Analytics Engine

This directory contains the Python backend for the **Material Availability & Inventory Replenishment (MAIR)** system.

It features a **pluggable enterprise connector framework** supporting **20+ enterprise data sources** (CSV, Excel, SQL Server, PostgreSQL, MySQL, Oracle, SAP ECC, SAP S/4HANA, SAP HANA, Microsoft Fabric Lakehouse/Warehouse, Azure SQL, Databricks, Snowflake, REST/OData APIs, SharePoint, S3/Azure Blob Storage), a **schema mapping engine**, a **data validation framework**, a **deterministic analytics engine**, an **MCP server**, a **Microsoft Agent Framework copilot**, and a **FastAPI gateway**.

---

## 🏗 Modular Architecture

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
     ┌────────────────┬───────────────┼───────────────┬────────────────┐
     ▼                ▼               ▼               ▼                ▼
CSV / Excel      SQL Databases       SAP         MS Fabric     REST/OData & Blob
(Pandas/OpenPyXL)(SQLAlchemy/pyodbc)(RFC/OData) (Lakehouse/SQL)  (Requests/S3)
```

### Key Invariants
1. **Source Agnostic Analytics**: The analytics engine receives **only** canonical Pydantic models (`Material`, `InventorySnapshot`, `BomLine`, `PurchaseOrder`, etc.). It never imports file readers, database drivers, SQL clients, or vendor SDKs.
2. **Pluggable Connectors**: Adding a new enterprise data connector requires creating a class inheriting from `BaseConnector` and decorating it with `@register_connector("name")`.
3. **Configurable Schema Mapping**: Convert enterprise column headers (e.g. SAP `MATNR`, `WERKS`, `LABST` or Custom `MaterialCode`) into canonical fields using JSON mapping files (`mappings/sap.json`, `mappings/fabric.json`, `mappings/sqlserver.json`).
4. **Data Quality Validation**: `ValidationEngine` checks for missing columns, null primary keys, duplicate keys, invalid dates, and negative inventory values.

---

## 📂 Codebase Layout

```
backend/
├── config/             # Settings (pydantic-settings & env config)
├── models/             # Canonical Pydantic schemas (models/canonical.py & models/schemas.py)
├── connectors/         # Enterprise Connector Framework
│   ├── base.py                 # BaseConnector ABC
│   ├── registry.py             # Global Connector Registry
│   ├── connector_factory.py    # Factory pattern for dynamic instantiation
│   ├── mapping_engine.py       # Enterprise column mapping engine
│   ├── validation_engine.py    # Schema compliance & quality validator
│   ├── caching.py              # Repository caching & streaming helpers
│   ├── csv_connector.py        # CSV file connector
│   ├── excel_connector.py      # Excel (.xlsx / .xls) connector
│   ├── sqlserver_connector.py  # SQL Server / Azure SQL connector
│   ├── postgres_connector.py   # PostgreSQL connector
│   ├── mysql_connector.py      # MySQL connector
│   ├── oracle_connector.py     # Oracle connector
│   ├── fabric_connector.py     # MS Fabric Lakehouse/Warehouse connector
│   ├── sap_connector.py        # SAP S/4HANA & ECC connector
│   ├── hana_connector.py       # SAP HANA database connector
│   ├── rest_connector.py       # REST / OData API connector
│   ├── blob_connector.py       # Cloud Object Storage (S3 / Azure Blob)
│   └── sharepoint_connector.py # SharePoint & OneDrive connector
├── mappings/           # Enterprise JSON column mapping rules
│   ├── sap.json
│   ├── fabric.json
│   ├── sqlserver.json
│   ├── csv.json
│   └── custom_company.json
├── repositories/       # Domain Repositories
│   ├── inventory_repository.py
│   ├── bom_repository.py
│   ├── supplier_repository.py
│   ├── production_repository.py
│   └── purchase_repository.py
├── data/               # Master Repository Facade (data/repository.py) & CSV baseline
├── analytics/          # Pure deterministic engine functions
├── mcp_server/         # Model Context Protocol stdio server
├── agents/             # 3 Agents + Orchestrator (Microsoft Agent Framework)
├── api/                # FastAPI app & route modules
├── persistence/        # SQLAlchemy database models & workflow state machine
├── services/           # Workflow orchestration & email notification engine
├── docs/               # Architecture & Migration guides (MIGRATION_GUIDE.md)
└── tests/              # Pytest suite (17 tests covering analytics, connectors, mappings)
```

---

## ⚡ Quick Start & Switch Data Sources

### 1. Run Baseline CSV Tests

```bash
pytest tests/ -v
```

All 17 unit and integration tests run without requiring external database or Azure OpenAI credentials.

### 2. Switch Data Source via `.env`

To switch from CSV to SQL Server, SAP, or Microsoft Fabric, change `DATA_SOURCE` in `.env`:

```ini
# Change data source:
DATA_SOURCE=sqlserver

# Configure database credentials:
SQLSERVER_CONNECTION_STRING=mssql+pyodbc://user:pass@sqlserver.corp.com/MAIR_DB?driver=ODBC+Driver+18+for+SQL+Server
```

Restart the FastAPI app:

```bash
uvicorn api.main:app --reload --port 8000
```

Zero code changes in analytics, MCP, agents, or API endpoints are required!

---

## 📘 Documentation

- See [docs/MIGRATION_GUIDE.md](file:///c:/Agentic%20AI/MAIR/backend/docs/MIGRATION_GUIDE.md) for step-by-step instructions on connecting SAP, Microsoft Fabric, SQL Server, REST APIs, or creating custom connectors.
