"""
Regenerate inventory_policies.csv and inventory.csv so every material has a
policy and inventory snapshot at EVERY plant where it is actually needed —
i.e. every plant whose BOM includes that material.

Root-cause: the original data was generated with one policy row per material
(assigned to a random plant) instead of one per material-per-plant-where-
consumed.  That left 62% of BOM-line × plant combos showing "No Data" in the
product BOM risk view.

Logic:
  - Canonical plant for a material = the plant already in the current data
    (preserve the existing numbers exactly so the answer key keeps passing).
  - For each additional plant that needs the material (because some product's
    BOM uses that material AND that product is produced at that plant):
      * avg_daily_usage  = canonical × Uniform(0.7, 1.4)   [±40% plant variation]
      * safety_stock_qty = canonical × Uniform(0.8, 1.25)
      * reorder_point_qty= avg_daily_usage * canonical_lead_time + new_safety_stock
      * max_stock_qty    = canonical × Uniform(0.85, 1.20)
      * reorder_qty      = canonical (same standard order qty)
    Inventory snapshot:
      * unrestricted_qty = Uniform(0.5 * new_rp, 2.0 * new_rp)
        — wide enough range to produce a realistic mix of statuses
      * quality_hold_qty = Uniform(0, 0.05 * unrestricted_qty)
      * blocked_qty      = Uniform(0, 0.02 * unrestricted_qty)
      * reserved_qty     = Uniform(0, 0.10 * unrestricted_qty)
      * snapshot_date    = today

Run from backend/:
    python scripts/regenerate_policies_and_inventory.py
"""
from __future__ import annotations

import csv
import random
from collections import defaultdict
from datetime import date
from pathlib import Path

SEED = 42
random.seed(SEED)

DATA = Path(__file__).resolve().parent.parent / "data" / "csv"


def load(name: str) -> list[dict]:
    return list(csv.DictReader(open(DATA / name)))


def save(name: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(DATA / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  Wrote {len(rows)} rows to {name}")


def main() -> None:
    plants_rows    = load("plants.csv")
    products_rows  = load("products.csv")
    bom_rows       = load("bom.csv")
    policies_rows  = load("inventory_policies.csv")
    inventory_rows = load("inventory.csv")
    sm_rows        = load("supplier_materials.csv")

    plant_ids = [r["plant_id"] for r in plants_rows]

    # Primary plant per product
    primary_plant = {r["product_id"]: r["primary_plant_id"] for r in products_rows}

    # Which plants need each material?
    # A plant needs a material if any product produced at that plant has the
    # material in its BOM.  We use primary_plant_id as the production assignment.
    material_needed_at: dict[str, set[str]] = defaultdict(set)
    for line in bom_rows:
        prod = line["product_id"]
        plant = primary_plant.get(prod)
        if plant:
            material_needed_at[line["material_id"]].add(plant)

    # Existing policy rows, keyed (material_id, plant_id)
    existing_policy: dict[tuple, dict] = {}
    for row in policies_rows:
        existing_policy[(row["material_id"], row["plant_id"])] = row

    # Existing inventory rows, keyed (material_id, plant_id)
    existing_inv: dict[tuple, dict] = {}
    for row in inventory_rows:
        existing_inv[(row["material_id"], row["plant_id"])] = row

    # Primary supplier lead time per material
    primary_lead: dict[str, int] = {}
    for sm in sm_rows:
        if sm["is_primary_supplier"].strip().lower() in ("true", "1", "yes"):
            primary_lead[sm["material_id"]] = int(sm["lead_time_days"])

    new_policies: list[dict] = list(policies_rows)   # start with all existing rows
    new_inventory: list[dict] = list(inventory_rows)

    added_policies = 0
    added_inventory = 0
    today = str(date.today())

    # Next policy/inventory ID counters (find max existing IDs)
    existing_pol_ids = [int(r.get("policy_id", "0").replace("POL-", "") or 0)
                        for r in policies_rows if r.get("policy_id", "").startswith("POL-")]
    pol_counter = max(existing_pol_ids, default=0) + 1

    existing_inv_ids = [int(r.get("inventory_id", "0").replace("INV-", "") or 0)
                        for r in inventory_rows if r.get("inventory_id", "").startswith("INV-")]
    inv_counter = max(existing_inv_ids, default=0) + 1

    # Warehouse per plant (pick first RM warehouse for that plant)
    warehouses = load("warehouses.csv")
    plant_warehouse: dict[str, str] = {}
    for wh in warehouses:
        pid = wh["plant_id"]
        if pid not in plant_warehouse:
            plant_warehouse[pid] = wh["warehouse_id"]

    for material_id, needed_plants in material_needed_at.items():
        # Find the canonical policy row (the one that already exists)
        canonical_key = next(
            ((material_id, pid) for pid in plant_ids if (material_id, pid) in existing_policy),
            None,
        )
        if canonical_key is None:
            # Material has no policy anywhere — skip (shouldn't happen given earlier check)
            continue

        canon_pol = existing_policy[canonical_key]
        lead_time = primary_lead.get(material_id, 14)

        canon_adu   = float(canon_pol["avg_daily_usage"])
        canon_ss    = float(canon_pol["safety_stock_qty"])
        canon_max   = float(canon_pol["max_stock_qty"])
        canon_reord = float(canon_pol["reorder_qty"])

        for plant_id in needed_plants:
            if (material_id, plant_id) in existing_policy:
                continue  # already have it

            # Generate per-plant variation
            adu  = round(canon_adu  * random.uniform(0.70, 1.40), 2)
            ss   = round(canon_ss   * random.uniform(0.80, 1.25), 2)
            rp   = round(adu * lead_time + ss, 2)
            mx   = round(canon_max  * random.uniform(0.85, 1.20), 2)
            reord = round(canon_reord, 2)

            # Build policy row using same fields as existing rows
            pol_row = dict(canon_pol)  # copy all fields (handles any extra columns)
            pol_row["material_id"]      = material_id
            pol_row["plant_id"]         = plant_id
            pol_row["avg_daily_usage"]  = adu
            pol_row["safety_stock_qty"] = ss
            pol_row["reorder_point_qty"]= rp
            pol_row["max_stock_qty"]    = mx
            pol_row["reorder_qty"]      = reord
            # If the CSV has a surrogate key column, assign a new one
            if "policy_id" in pol_row:
                pol_row["policy_id"] = f"POL-{pol_counter:05d}"
                pol_counter += 1

            new_policies.append(pol_row)
            existing_policy[(material_id, plant_id)] = pol_row
            added_policies += 1

            # Generate inventory snapshot if one doesn't exist
            if (material_id, plant_id) not in existing_inv:
                # Uniform over [0.5*rp, 2.0*rp] — wide range for status variety
                unrestricted = round(random.uniform(0.5 * rp, 2.0 * rp), 2)
                qh  = round(random.uniform(0, 0.05 * unrestricted), 2)
                blk = round(random.uniform(0, 0.02 * unrestricted), 2)
                res = round(random.uniform(0, 0.10 * unrestricted), 2)

                wh_id = plant_warehouse.get(plant_id, "WH-01")

                inv_row = {}
                # Mirror field order from existing rows
                sample_inv = inventory_rows[0]
                for field in sample_inv.keys():
                    inv_row[field] = ""
                inv_row["material_id"]     = material_id
                inv_row["plant_id"]        = plant_id
                inv_row["warehouse_id"]    = wh_id
                inv_row["unrestricted_qty"]= unrestricted
                inv_row["quality_hold_qty"]= qh
                inv_row["blocked_qty"]     = blk
                inv_row["reserved_qty"]    = res
                # Handle various possible date column names
                for date_field in ("snapshot_date", "last_count_date", "count_date"):
                    if date_field in inv_row:
                        inv_row[date_field] = today
                if "inventory_id" in inv_row:
                    inv_row["inventory_id"] = f"INV-{inv_counter:05d}"
                    inv_counter += 1

                new_inventory.append(inv_row)
                existing_inv[(material_id, plant_id)] = inv_row
                added_inventory += 1

    print(f"Added {added_policies} new policy rows  (was {len(policies_rows)}, now {len(new_policies)})")
    print(f"Added {added_inventory} new inventory rows (was {len(inventory_rows)}, now {len(new_inventory)})")

    # Write back
    pol_fields = list(policies_rows[0].keys())
    inv_fields = list(inventory_rows[0].keys())

    # Sort for determinism: by material_id, then plant_id
    new_policies.sort(key=lambda r: (r["material_id"], r["plant_id"]))
    new_inventory.sort(key=lambda r: (r["material_id"], r["plant_id"]))

    save("inventory_policies.csv", new_policies, pol_fields)
    save("inventory.csv",          new_inventory, inv_fields)
    print("Done.")


if __name__ == "__main__":
    main()
