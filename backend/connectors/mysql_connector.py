"""
MySQL Connector.
"""
from __future__ import annotations

from connectors.sqlserver_connector import SqlServerConnector
from connectors.registry import register_connector


@register_connector("mysql")
class MySqlConnector(SqlServerConnector):
    """MySQL relational database connector."""
    pass
