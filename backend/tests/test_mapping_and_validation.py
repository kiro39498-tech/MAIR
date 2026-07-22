"""
Unit tests for Schema Mapping Engine & Data Validation Framework.
"""
import pytest
from connectors.mapping_engine import MappingEngine
from connectors.validation_engine import ValidationEngine
from models.canonical import Material, InventorySnapshot


def test_mapping_engine_sap_conversion():
    sap_mapping = {
        "materials": {
            "MATNR": "material_id",
            "MAKTX": "material_name",
            "MEINS": "unit_of_measure"
        }
    }
    engine = MappingEngine(sap_mapping)
    raw_record = {"MATNR": "RM-101", "MAKTX": "Steel Sheet", "MEINS": "KG"}
    mapped = engine.map_record("materials", raw_record)

    assert mapped["material_id"] == "RM-101"
    assert mapped["material_name"] == "Steel Sheet"
    assert mapped["unit_of_measure"] == "KG"


def test_validation_engine_reports_errors():
    raw_records = [
        {"material_id": "M1", "material_name": "Mat 1", "material_type": "RAW"},
        {"material_id": None, "material_name": "Invalid Mat"},  # Null primary key
    ]

    valid, report = ValidationEngine.validate_records("materials", raw_records, Material)

    assert len(valid) == 1
    assert report.is_valid is False
    assert report.error_count == 1
    assert report.errors[0].error_type == "null_primary_key"


def test_validation_engine_flags_negative_inventory():
    raw_records = [
        {
            "material_id": "M1",
            "plant_id": "P001",
            "warehouse_id": "WH01",
            "unrestricted_qty": -10.0,
            "quality_hold_qty": 0.0,
            "blocked_qty": 0.0,
            "reserved_qty": 0.0,
            "snapshot_date": "2026-01-01"
        }
    ]

    valid, report = ValidationEngine.validate_records("inventory", raw_records, InventorySnapshot)
    assert report.warning_count >= 1
    assert any(w.error_type == "negative_inventory" for w in report.warnings)
