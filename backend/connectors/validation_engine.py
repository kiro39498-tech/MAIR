"""
Data Validation Framework for enterprise connector payloads.

Performs schema compliance checks, null primary key validation, duplicate key detection,
date parsing validation, and negative inventory flags.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Any, Type, Set
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationErrorDetail:
    entity_name: str
    record_index: int
    field_name: str
    error_type: str  # 'missing_field', 'null_primary_key', 'duplicate_pk', 'negative_inventory', 'invalid_date'
    message: str


@dataclass
class ValidationReport:
    is_valid: bool = True
    total_records: int = 0
    valid_records: int = 0
    error_count: int = 0
    warning_count: int = 0
    errors: List[ValidationErrorDetail] = field(default_factory=list)
    warnings: List[ValidationErrorDetail] = field(default_factory=list)

    def add_error(self, detail: ValidationErrorDetail):
        self.errors.append(detail)
        self.error_count += 1
        self.is_valid = False

    def add_warning(self, detail: ValidationErrorDetail):
        self.warnings.append(detail)
        self.warning_count += 1


class ValidationEngine:
    """Enterprise Data Validation Engine."""

    PRIMARY_KEYS = {
        "materials": ["material_id"],
        "plants": ["plant_id"],
        "warehouses": ["warehouse_id"],
        "suppliers": ["supplier_id"],
        "products": ["product_id"],
        "inventory": ["material_id", "plant_id"],
        "inventory_policies": ["material_id", "plant_id"],
        "purchase_orders": ["po_id", "po_line"],
        "production_orders": ["production_order_id"],
        "bom": ["bom_id"],
    }

    @classmethod
    def validate_records(
        cls, entity_name: str, records: List[Dict[str, Any]], model_cls: Type[BaseModel]
    ) -> tuple[List[Dict[str, Any]], ValidationReport]:
        """Validate raw dictionary records against pydantic canonical model and domain rules."""
        report = ValidationReport(total_records=len(records))
        valid_records = []
        seen_pks: Set[tuple] = set()

        pk_fields = cls.PRIMARY_KEYS.get(entity_name, [])

        for idx, rec in enumerate(records):
            record_valid = True

            # 1. Primary key null / presence check
            pk_tuple = []
            for pk_field in pk_fields:
                val = rec.get(pk_field)
                if val is None or str(val).strip() == "":
                    report.add_error(
                        ValidationErrorDetail(
                            entity_name=entity_name,
                            record_index=idx,
                            field_name=pk_field,
                            error_type="null_primary_key",
                            message=f"Record {idx} has null or empty primary key '{pk_field}'"
                        )
                    )
                    record_valid = False
                else:
                    pk_tuple.append(str(val).strip())

            # Skip schema parsing if primary key is already missing/invalid
            if not record_valid:
                continue

            # 2. Duplicate primary key check
            if pk_tuple:
                pk_key = tuple(pk_tuple)
                if pk_key in seen_pks:
                    report.add_warning(
                        ValidationErrorDetail(
                            entity_name=entity_name,
                            record_index=idx,
                            field_name=",".join(pk_fields),
                            error_type="duplicate_pk",
                            message=f"Duplicate primary key {pk_key} found at record {idx}"
                        )
                    )
                else:
                    seen_pks.add(pk_key)

            # 3. Domain specific validation: Negative inventory check
            if entity_name == "inventory":
                for qty_field in ("unrestricted_qty", "quality_hold_qty", "blocked_qty", "reserved_qty"):
                    val = rec.get(qty_field, 0.0)
                    try:
                        if float(val) < 0:
                            report.add_warning(
                                ValidationErrorDetail(
                                    entity_name=entity_name,
                                    record_index=idx,
                                    field_name=qty_field,
                                    error_type="negative_inventory",
                                    message=f"Negative inventory value ({val}) for {qty_field} at index {idx}"
                                )
                            )
                    except (ValueError, TypeError):
                        pass

            # 4. Pydantic canonical model validation
            try:
                sanitized = cls._sanitize_dates(rec, model_cls)
                model_cls(**sanitized)
                valid_records.append(sanitized)
                report.valid_records += 1
            except ValidationError as ve:
                report.add_error(
                    ValidationErrorDetail(
                        entity_name=entity_name,
                        record_index=idx,
                        field_name="general",
                        error_type="invalid_schema",
                        message=f"Schema validation error at index {idx}: {ve}"
                    )
                )

        return valid_records, report

    @staticmethod
    def _sanitize_dates(rec: Dict[str, Any], model_cls: Type[BaseModel]) -> Dict[str, Any]:
        """Convert ISO date strings or datetime objects to python date/datetime if model requires it."""
        sanitized = rec.copy()
        for field_name, field_info in model_cls.model_fields.items():
            val = sanitized.get(field_name)
            if val and isinstance(val, str):
                if "date" in field_name or field_name.endswith("_at"):
                    try:
                        if "T" in val:
                            sanitized[field_name] = datetime.fromisoformat(val.replace("Z", "+00:00")).date()
                        elif "-" in val and len(val) == 10:
                            sanitized[field_name] = date.fromisoformat(val)
                    except ValueError:
                        pass
        return sanitized
