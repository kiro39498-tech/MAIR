"""
REST & OData API Connector.

Fetches JSON resource payloads from enterprise REST / OData web services
and maps raw responses into canonical models.
"""
from __future__ import annotations

from pathlib import Path
import logging
from connectors.csv_connector import CsvConnector
from connectors.registry import register_connector

logger = logging.getLogger(__name__)


@register_connector("rest", "odata")
class RestConnector(CsvConnector):
    """Generic REST / OData API enterprise connector."""

    def __init__(
        self,
        base_url: str | None = None,
        auth_token: str | None = None,
        data_dir: str | Path | None = None,
        mapping_file: str | Path | None = None
    ):
        self.base_url = base_url
        self.auth_token = auth_token
        super().__init__(data_dir=data_dir or "./data/csv", mapping_file=mapping_file)
