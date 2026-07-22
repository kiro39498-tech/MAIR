"""
Connector Registry for dynamic connector registration and lookup.
"""
from __future__ import annotations

import logging
from typing import Type, Dict
from connectors.base import BaseConnector

logger = logging.getLogger(__name__)

_CONNECTOR_REGISTRY: Dict[str, Type[BaseConnector]] = {}


def register_connector(*names: str):
    """Decorator to register a connector class under one or more target source names."""
    def decorator(cls: Type[BaseConnector]):
        for name in names:
            key = name.strip().lower()
            _CONNECTOR_REGISTRY[key] = cls
            logger.debug(f"Registered connector '{cls.__name__}' for source '{key}'")
        return cls
    return decorator


def get_connector_class(source_name: str) -> Type[BaseConnector]:
    """Retrieve the connector class registered for a given source name."""
    key = source_name.strip().lower()
    if key not in _CONNECTOR_REGISTRY:
        # Lazy import of default connectors if registry is empty or missing key
        _ensure_connectors_loaded()

    if key not in _CONNECTOR_REGISTRY:
        available = list(_CONNECTOR_REGISTRY.keys())
        raise ValueError(
            f"Unsupported data source '{source_name}'. "
            f"Registered sources: {available}"
        )
    return _CONNECTOR_REGISTRY[key]


def list_registered_connectors() -> list[str]:
    """Return a list of all currently registered data source names."""
    _ensure_connectors_loaded()
    return sorted(list(_CONNECTOR_REGISTRY.keys()))


def _ensure_connectors_loaded():
    """Import all connector implementations to ensure decorator registration executes."""
    try:
        import connectors.csv_connector
        import connectors.excel_connector
        import connectors.sqlserver_connector
        import connectors.postgres_connector
        import connectors.mysql_connector
        import connectors.oracle_connector
        import connectors.fabric_connector
        import connectors.sap_connector
        import connectors.hana_connector
        import connectors.rest_connector
        import connectors.blob_connector
        import connectors.sharepoint_connector
    except ImportError as e:
        logger.warning(f"Some connector modules could not be imported lazily: {e}")
