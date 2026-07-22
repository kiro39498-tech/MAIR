"""
Cloud Storage Connector (AWS S3 / Azure Blob Storage).
"""
from __future__ import annotations

from pathlib import Path
import logging
from connectors.csv_connector import CsvConnector
from connectors.registry import register_connector

logger = logging.getLogger(__name__)


@register_connector("blob", "s3", "azure_blob")
class BlobConnector(CsvConnector):
    """Cloud object storage connector for S3 buckets and Azure Blob Storage containers."""

    def __init__(
        self,
        connection_string: str | None = None,
        container_name: str | None = None,
        data_dir: str | Path | None = None,
        mapping_file: str | Path | None = None
    ):
        self.connection_string = connection_string
        self.container_name = container_name
        super().__init__(data_dir=data_dir or "./data/csv", mapping_file=mapping_file)
