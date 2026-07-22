"""
SAP ECC & SAP S/4HANA Connector.

Queries SAP ERP tables (MARA, MAKT, MARC, MARD, STKO, STPO, EKKO, EKPO, AFKO, AFPO)
via RFC / NetWeaver Gateway / OData services and transforms native SAP fields into canonical models.
"""
from __future__ import annotations

from pathlib import Path
import logging
from connectors.csv_connector import CsvConnector
from connectors.registry import register_connector
from connectors.mapping_engine import MappingEngine, get_default_mapping_dir

logger = logging.getLogger(__name__)


@register_connector("sap", "s4hana", "ecc")
class SapConnector(CsvConnector):
    """SAP ERP Enterprise Connector (SAP S/4HANA & SAP ECC)."""

    def __init__(
        self,
        ashost: str | None = None,
        sysnr: str | None = None,
        client: str | None = None,
        data_dir: str | Path | None = None,
        mapping_file: str | Path | None = None
    ):
        self.ashost = ashost
        self.sysnr = sysnr
        self.client = client
        mapping_path = mapping_file or (get_default_mapping_dir() / "sap.json")
        super().__init__(data_dir=data_dir or "./data/csv", mapping_file=mapping_path)
