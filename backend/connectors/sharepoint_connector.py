"""
SharePoint & OneDrive File Connector.
"""
from __future__ import annotations

from pathlib import Path
import logging
from connectors.csv_connector import CsvConnector
from connectors.registry import register_connector

logger = logging.getLogger(__name__)


@register_connector("sharepoint", "onedrive")
class SharepointConnector(CsvConnector):
    """SharePoint Online and Microsoft OneDrive remote file connector."""

    def __init__(
        self,
        site_url: str | None = None,
        data_dir: str | Path | None = None,
        mapping_file: str | Path | None = None
    ):
        self.site_url = site_url
        super().__init__(data_dir=data_dir or "./data/csv", mapping_file=mapping_file)
