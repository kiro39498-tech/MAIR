"""
Enterprise Connector Factory (SSOT Section 6, Factory Pattern).

Instantiates the active connector based on environment configuration or explicit parameters.
The analytics engine, MCP tools, multi-agent systems, and REST API layers call this factory
and never know or care which connector implementation is running.
"""
from __future__ import annotations

import logging
from typing import Optional, Dict
from connectors.base import BaseConnector
from connectors.registry import get_connector_class
from config.settings import settings

logger = logging.getLogger(__name__)

_CONNECTOR_INSTANCES: Dict[str, BaseConnector] = {}


class ConnectorFactory:
    """Factory for creating and caching pluggable enterprise data connectors."""

    @staticmethod
    def create(data_source: Optional[str] = None, force_new: bool = False, **kwargs) -> BaseConnector:
        """Create or return a cached instance of the configured data connector.

        Args:
            data_source: Data source identifier (e.g. 'csv', 'sqlserver', 'sap', 'fabric').
                         Defaults to settings.data_source if not specified.
            force_new: If True, bypasses cached instances and creates a fresh connector.
            kwargs: Additional parameters passed to the connector constructor.

        Returns:
            An instance implementing BaseConnector.
        """
        source_key = (data_source or settings.data_source).strip().lower()

        if not force_new and source_key in _CONNECTOR_INSTANCES:
            return _CONNECTOR_INSTANCES[source_key]

        connector_cls = get_connector_class(source_key)

        # Build connector-specific constructor arguments from settings / kwargs
        init_kwargs = ConnectorFactory._build_connector_kwargs(source_key, kwargs)
        
        logger.info(f"Instantiating '{connector_cls.__name__}' for data source '{source_key}'")
        instance = connector_cls(**init_kwargs)

        if not force_new:
            _CONNECTOR_INSTANCES[source_key] = instance

        return instance

    @staticmethod
    def _build_connector_kwargs(source_key: str, user_kwargs: dict) -> dict:
        """Extract settings appropriate for the specified source key."""
        merged = user_kwargs.copy()
        
        if source_key in ("csv", "csv_connector"):
            if "data_dir" not in merged:
                merged["data_dir"] = settings.csv_data_dir
        elif source_key in ("excel", "excel_connector"):
            if "excel_file" not in merged:
                merged["excel_file"] = getattr(settings, "excel_file", None)
            if "data_dir" not in merged:
                merged["data_dir"] = settings.csv_data_dir
        elif source_key in ("sqlserver", "ssms", "postgres", "postgresql", "mysql", "oracle", "azuresql"):
            if "connection_string" not in merged:
                merged["connection_string"] = getattr(settings, f"{source_key}_connection_string", None)
        elif source_key in ("fabric", "fabric_lakehouse", "fabric_warehouse", "snowflake", "databricks"):
            if "workspace_id" not in merged:
                merged["workspace_id"] = getattr(settings, "fabric_workspace_id", None)
            if "connection_string" not in merged:
                merged["connection_string"] = getattr(settings, "fabric_connection_string", None)
        elif source_key in ("sap", "s4hana", "ecc", "hana"):
            if "ashost" not in merged:
                merged["ashost"] = getattr(settings, "sap_ashost", None)

        return merged

    @staticmethod
    def clear_cache():
        """Clear cached connector instances (useful for testing or switching sources)."""
        _CONNECTOR_INSTANCES.clear()
