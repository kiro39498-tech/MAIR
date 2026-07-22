"""
Oracle Database Connector.
"""
from __future__ import annotations

from connectors.sqlserver_connector import SqlServerConnector
from connectors.registry import register_connector


@register_connector("oracle")
class OracleConnector(SqlServerConnector):
    """Oracle Database enterprise connector."""
    pass
