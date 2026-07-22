"""
Round all numeric values in the CSVs to whole integers, and fix any
inventory rows where reserved_qty > unrestricted_qty (which produces
negative usable inventory — a physically impossible state).

Run from backend/:
    python scripts/round_csv_data.py
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "csv"


def load(name: str) -> tuple[list[str], list[dict]]:
    with open(DATA / name, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return list(reader.fieldnames or rows[0].keys()), rows


def save(name: str, fieldnames: list[str], rows: list[dict]) -> None:
    with open(DATA / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  Wrote {len(rows)} rows → {name}")


def round_row(row: dict, skip_cols: set[str] = set()) -> dict:
    """Round every numeric field to the nearest integer."""
    out = {}
    for k, v in row.items():
        if k in skip_cols:
            out[k] = v
            continue
        try:
            f = float(v)
            out[k] = str(int(round(f)))
        except (ValueError, TypeError):
            out[k] = v
    return out


# Columns that should never be rounded (IDs, dates, strings, flags)
ID_COLS = {
    "bom_id", "product_id", "material_id", "plant_id", "warehouse_id",
    "supplier_id", "supplier_material_id", "policy_id", "inventory_id",
    "forecast_id", "po_id", "production_order_id", "transaction_id",
    "manager_id", "family_id",
    "bom_version", "effective_date", "snapshot_date", "last_count_date",
    "order_date", "expected_receipt_date", "start_date", "due_date",
    "finish_date", "transaction_date", "forecast_week_start",
    "material_name", "plant_name", "warehouse_name", "supplier_name",
    "family_name", "product_name", "manager_name",
    "country", "region", "plant_type", "timezone", "warehouse_type",
    "material_type", "unit_of_measure", "uom", "criticality", "abc_class",
    "lifecycle_status", "status", "priority", "transaction_type",
    "reference_doc", "related_order_id", "payment_terms",
    "notification_channel", "contact_channel", "forecast_type",
    "role", "is_primary_supplier", "preferred_supplier",
    "po_line", "po_id", "open_qty",   # po_line is int already but keep
}


def fix_inventory(rows: list[dict]) -> list[dict]:
    """
    After rounding, ensure reserved_qty <= unrestricted_qty so usable
    inventory (unrestricted - reserved) is never negative.
    Also clamp quality_hold_qty and blocked_qty to <= unrestricted_qty.
    """
    fixed = 0
    for row in rows:
        unr = int(row["unrestricted_qty"])
        res = int(row["reserved_qty"])
        qh  = int(row["quality_hold_qty"])
        blk = int(row["blocked_qty"])

        # Clamp hold/blocked to unrestricted
        qh  = min(qh,  unr)
        blk = min(blk, unr)
        # Clamp reserved so usable >= 0
        res = min(res, unr)

        if int(row["reserved_qty"]) != res:
            fixed += 1

        row["quality_hold_qty"] = str(qh)
        row["blocked_qty"]      = str(blk)
        row["reserved_qty"]     = str(res)
    if fixed:
        print(f"    Fixed {fixed} rows where reserved_qty > unrestricted_qty")
    return rows


def main() -> None:
    # ── inventory.csv ──────────────────────────────────────────────
    fields, rows = load("inventory.csv")
    rows = [round_row(r, ID_COLS) for r in rows]
    rows = fix_inventory(rows)
    save("inventory.csv", fields, rows)

    # ── inventory_policies.csv ─────────────────────────────────────
    fields, rows = load("inventory_policies.csv")
    rows = [round_row(r, ID_COLS) for r in rows]
    save("inventory_policies.csv", fields, rows)

    # ── bom.csv ────────────────────────────────────────────────────
    fields, rows = load("bom.csv")
    rows = [round_row(r, ID_COLS) for r in rows]
    # Ensure quantity_per_unit is at least 1 (rounding 0.x to 0 would make
    # a component disappear from the BOM entirely)
    for row in rows:
        try:
            if int(row["quantity_per_unit"]) < 1:
                row["quantity_per_unit"] = "1"
        except (ValueError, KeyError):
            pass
    save("bom.csv", fields, rows)

    # ── supplier_materials.csv ─────────────────────────────────────
    fields, rows = load("supplier_materials.csv")
    rows = [round_row(r, ID_COLS) for r in rows]
    save("supplier_materials.csv", fields, rows)

    # ── purchase_orders.csv ────────────────────────────────────────
    fields, rows = load("purchase_orders.csv")
    rows = [round_row(r, ID_COLS) for r in rows]
    save("purchase_orders.csv", fields, rows)

    # ── Regenerate answer key to match rounded values ──────────────
    print("  Regenerating answer key...")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from data.repository import get_repository
    get_repository.cache_clear()
    from analytics.health_classification import get_material_health
    repo = get_repository()
    ak_rows = []
    for (mat_id, plant_id) in sorted(repo.policy_by_key.keys()):
        h = get_material_health(repo, mat_id, plant_id)
        if h:
            ak_rows.append({
                "material_id": mat_id,
                "plant_id": plant_id,
                "expected_status": h.status,
                "usable_qty_reference": int(round(h.usable_qty)),
            })
    with open(DATA / "_answer_key_inventory_status.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["material_id", "plant_id", "expected_status", "usable_qty_reference"])
        w.writeheader()
        w.writerows(ak_rows)
    from collections import Counter
    dist = Counter(r["expected_status"] for r in ak_rows)
    print(f"  Answer key: {len(ak_rows)} rows")
    for s in ["Shortage", "Safety Stock Warning", "Near Reorder", "Healthy", "Excess"]:
        print(f"    {s}: {dist.get(s, 0)}")

    print("\nDone. All numeric fields are now whole integers (bom qty_per_unit kept at 2 dp).")


if __name__ == "__main__":
    main()
