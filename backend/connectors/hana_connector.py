"""
SAP HANA In-Memory Database Connector.
"""
from __future__ import annotations

from connectors.sap_connector import SapConnector
from connectors.registry import register_connector


@register_connector("hana")
class HanaConnector(SapConnector):
    """SAP HANA in-memory database connector."""
    pass
