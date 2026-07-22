"""
Schema Mapping Engine for enterprise column transformations.

Translates source enterprise column headers (e.g., SAP MATNR, WERKS, LABST,
or Custom Enterprise MaterialCode) into canonical field names.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MappingEngine:
    """Schema Mapping Engine converting enterprise column names to canonical schema fields."""

    def __init__(self, mapping_rules: Optional[Dict[str, Dict[str, str]]] = None):
        """
        mapping_rules dictionary structure:
        {
            "materials": {"MATNR": "material_id", "MAKTX": "material_name", ...},
            "inventory": {"WERKS": "plant_id", "LABST": "unrestricted_qty", ...},
            ...
        }
        """
        self.mapping_rules: Dict[str, Dict[str, str]] = mapping_rules or {}

    @classmethod
    def load_from_file(cls, filepath: str | Path) -> MappingEngine:
        """Load mapping rules from a JSON configuration file."""
        path = Path(filepath)
        if not path.exists():
            logger.warning(f"Mapping file not found: {path}. Using identity mapping.")
            return cls({})
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(data)
        except Exception as e:
            logger.error(f"Failed to load mapping file {path}: {e}")
            return cls({})

    def map_record(self, entity_name: str, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single record dict using entity-specific mapping rules."""
        rules = self.mapping_rules.get(entity_name, {})
        if not rules:
            return raw_record

        mapped = {}
        for key, value in raw_record.items():
            canonical_key = rules.get(key, key)
            mapped[canonical_key] = value
        return mapped

    def map_records(self, entity_name: str, records: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """Transform a list of record dicts."""
        rules = self.mapping_rules.get(entity_name, {})
        if not rules:
            return records
        return [self.map_record(entity_name, r) for r in records]


def get_default_mapping_dir() -> Path:
    """Return the absolute path to the backend mappings directory."""
    return Path(__file__).resolve().parent.parent / "mappings"
