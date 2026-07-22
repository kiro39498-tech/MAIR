"""
PostgreSQL Connector.
"""
from __future__ import annotations

from pathlib import Path
import logging
from connectors.sqlserver_connector import SqlServerConnector
from connectors.registry import register_connector

logger = logging.getLogger(__name__)


@register_connector("postgres", "postgresql")
class PostgresConnector(SqlServerConnector):
    """PostgreSQL relational database connector extending SqlServerConnector abstraction."""
    pass
