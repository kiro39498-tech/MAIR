"""
Regenerate _answer_key_inventory_status.csv to match the canonical
health classification logic (using reorder_point_qty from the policy CSV
directly, without the spurious lead-time re-adjustment that was inflating
most materials into Safety Stock Warning).

Also covers the new policy rows added by regenerate_policies_and_inventory.py.

Run from backend/:
    python scripts/regenerate_answer_key.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.repository import get_repository
from analytics.health_classification import get_material_health


def main() -> None:
    # Clear lru_cache in case the module was already imported with old data
    from data.repository import get_repository as _gr
    _gr.cache_clear()

    repo = get_repository()
    rows = []

    for (mat_id, plant_id) in sorted(repo.policy_by_key.keys()):
        h = get_material_health(repo, mat_id, plant_id)
        if h:
            rows.append({
                "material_id": mat_id,
                "plant_id": plant_id,
                "expected_status": h.status,
                "usable_qty_reference": round(h.usable_qty, 2),
            })

    out_path = Path(__file__).resolve().parent.parent / "data" / "csv" / "_answer_key_inventory_status.csv"
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["material_id", "plant_id", "expected_status", "usable_qty_reference"])
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    dist = Counter(r["expected_status"] for r in rows)
    print(f"Wrote {len(rows)} rows to _answer_key_inventory_status.csv")
    print("Status distribution:")
    for s in ["Shortage", "Safety Stock Warning", "Near Reorder", "Healthy", "Excess"]:
        n = dist.get(s, 0)
        print(f"  {s:25s}: {n:4d}  ({n/len(rows)*100:.1f}%)")


if __name__ == "__main__":
    main()
