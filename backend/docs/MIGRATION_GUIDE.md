# Enterprise Data Connector Migration Guide

This guide explains how to migrate your **Material Availability & Inventory Replenishment (MAIR)** backend from the default CSV file data source to an enterprise data provider (SQL Server, SAP S/4HANA, Microsoft Fabric Lakehouse, Excel, PostgreSQL, Oracle, REST APIs, or Blob Storage).

---

## 🎯 Architecture Principles

The MAIR architecture follows strict separation of concerns:

- **Analytics Engine**: Operates exclusively on canonical Pydantic data models (`Material`, `InventorySnapshot`, `BomLine`, `PurchaseOrder`, etc.). It **never** executes SQL queries, imports database drivers, or accesses CSV files directly.
- **Repository Layer**: Composes domain repositories (`InventoryRepository`, `BomRepository`, `SupplierRepository`, `ProductionRepository`, `PurchaseRepository`) and delegates data loading to `ConnectorFactory.create()`.
- **Connector Framework**: Pluggable connectors map enterprise schemas into canonical models using the `MappingEngine` and validate data using `ValidationEngine`.

Changing the data source requires **zero code changes** in the analytics engine, MCP server, multi-agent copilot, or FastAPI endpoints. You only update configuration settings in `.env`.

---

## 🛠 Supported Connectors

| Data Source | `DATA_SOURCE` Value | Required Settings |
| :--- | :--- | :--- |
| **CSV Files** | `csv` | `CSV_DATA_DIR=./data/csv` |
| **Excel Workbook** | `excel` | `EXCEL_FILE=./data/supply_chain.xlsx` |
| **SQL Server / SSMS** | `sqlserver` | `SQLSERVER_CONNECTION_STRING=mssql+pyodbc://...` |
| **PostgreSQL** | `postgres` | `DATABASE_URL=postgresql://user:pass@localhost:5432/mair` |
| **MySQL** | `mysql` | `DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/mair` |
| **Oracle** | `oracle` | `DATABASE_URL=oracle+oracledb://user:pass@localhost:1521/mair` |
| **Microsoft Fabric** | `fabric` | `FABRIC_WORKSPACE_ID=...`, `FABRIC_CONNECTION_STRING=...` |
| **SAP S/4HANA / ECC** | `sap` | `SAP_ASHOST=192.168.1.50`, `SAP_CLIENT=100`, `SAP_USER=...` |
| **SAP HANA** | `hana` | `DATABASE_URL=hana://user:pass@host:30015` |
| **REST / OData API** | `rest` | `REST_BASE_URL=https://api.enterprise.com/v1` |
| **Cloud Storage** | `blob` | `BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https...` |
| **SharePoint** | `sharepoint` | `SHAREPOINT_SITE_URL=https://company.sharepoint.com/...` |

---

## 🚀 Step-by-Step Migration Examples

### 1. Migrating to Microsoft SQL Server / Azure SQL

1. **Install database driver**:
   ```bash
   pip install sqlalchemy pyodbc
   ```

2. **Configure `.env`**:
   ```ini
   DATA_SOURCE=sqlserver
   SQLSERVER_CONNECTION_STRING=mssql+pyodbc://app_user:StrongPassword@sql-server.company.com/MAIR_DB?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no
   ```

3. **Schema Column Mapping** (`backend/mappings/sqlserver.json`):
   ```json
   {
     "materials": {
       "MaterialCode": "material_id",
       "MaterialName": "material_name",
       "Type": "material_type",
       "UnitOfMeasure": "unit_of_measure"
     },
     "inventory": {
       "MaterialCode": "material_id",
       "PlantCode": "plant_id",
       "AvailableQty": "unrestricted_qty",
       "HoldQty": "quality_hold_qty"
     }
   }
   ```

4. **Restart Backend**:
   ```bash
   uvicorn api.main:app --reload
   ```

---

### 2. Migrating to Microsoft Fabric Lakehouse / Warehouse

1. **Configure `.env`**:
   ```ini
   DATA_SOURCE=fabric
   FABRIC_WORKSPACE_ID=3f8a002b-8a4d-4e9b-b9f1-7c9812ab0011
   FABRIC_CONNECTION_STRING=mssql+pyodbc://@powerbi://api.powerbi.com/v1.0/myorg/MAIR_Workspace?driver=ODBC+Driver+18+for+SQL+Server
   ```

2. **Schema Column Mapping** (`backend/mappings/fabric.json`):
   ```json
   {
     "materials": {
       "MaterialSK": "material_id",
       "MaterialDescription": "material_name",
       "Category": "material_type"
     },
     "inventory": {
       "MaterialSK": "material_id",
       "FacilityID": "plant_id",
       "OnHandQty": "unrestricted_qty",
       "AllocatedQty": "reserved_qty"
     }
   }
   ```

---

### 3. Migrating to SAP S/4HANA / ECC

1. **Configure `.env`**:
   ```ini
   DATA_SOURCE=sap
   SAP_ASHOST=sap-prd.corp.company.com
   SAP_SYSNR=00
   SAP_CLIENT=100
   SAP_USER=MAIR_SERVICE_ACCT
   SAP_PASSWORD=SecretPassword123
   ```

2. **Native SAP Field Mapping** (`backend/mappings/sap.json`):
   - `MATNR` $\rightarrow$ `material_id`
   - `MAKTX` $\rightarrow$ `material_name`
   - `WERKS` $\rightarrow$ `plant_id`
   - `LABST` $\rightarrow$ `unrestricted_qty`
   - `INSME` $\rightarrow$ `quality_hold_qty`
   - `SPEME` $\rightarrow$ `blocked_qty`

---

## ➕ Adding a Custom Enterprise Connector

Adding a custom connector requires only 3 steps:

1. **Create `backend/connectors/custom_connector.py`**:
   ```python
   from connectors.base import BaseConnector
   from connectors.registry import register_connector
   from models.canonical import Material, InventorySnapshot

   @register_connector("custom_system")
   class CustomSystemConnector(BaseConnector):
       def __init__(self, api_key: str = None, **kwargs):
           self.api_key = api_key

       def load_materials( me ) -> list[Material]:
           # Fetch records from custom system SDK / API
           raw_records = fetch_from_custom_api()
           return [Material(**r) for r in raw_records]

       def load_inventory(self) -> list[InventorySnapshot]:
           # Implement loading
           ...
   ```

2. **Register source key in `.env`**:
   ```ini
   DATA_SOURCE=custom_system
   ```

3. **Restart the server**. The analytics engine, MCP server, agents, and FastAPI routes will immediately begin utilizing your custom connector!
