"""
Microsoft Fabric Lakehouse / Warehouse / SQL Endpoint Connector.

Queries Microsoft Fabric OneLake Delta tables or Fabric SQL Endpoints,
transforming enterprise cloud data warehouse entities into canonical models.
"""
from __future__ import annotations

from pathlib import Path
import logging
from connectors.sqlserver_connector import SqlServerConnector
from connectors.registry import register_connector
from connectors.mapping_engine import MappingEngine, get_default_mapping_dir

logger = logging.getLogger(__name__)


@register_connector("fabric", "fabric_lakehouse", "fabric_warehouse", "snowflake", "databricks")
class FabricConnector(SqlServerConnector):
    """Microsoft Fabric & Cloud Data Platform connector (Fabric Lakehouse / Warehouse / Snowflake / Databricks)."""

    def __init__(
        self,
        workspace_id: str | None = None,
        connection_string: str | None = None,
        data_dir: str | Path | None = None,
        mapping_file: str | Path | None = None
    ):
        self.workspace_id = workspace_id
        mapping_path = mapping_file or (get_default_mapping_dir() / "fabric.json")
        super().__init__(connection_string=connection_string, data_dir=data_dir, mapping_file=mapping_path)
