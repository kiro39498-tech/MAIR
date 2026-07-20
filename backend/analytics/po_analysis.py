"""
Open purchase order analysis — does incoming supply actually cover the
shortfall, and is it arriving on time?
"""
from __future__ import annotations

from datetime import date

from data.repository import Repository
from models.schemas import PoCoverage
from analytics.projection import project_material_balance


def analyze_po_coverage(repo: Repository, material_id: str, plant_id: str) -> PoCoverage:
    open_pos = repo.open_pos_by_material_plant.get((material_id, plant_id), [])
    open_qty = sum(po.open_qty for po in open_pos)
    has_late_po = any(po.status == "Late" or po.expected_receipt_date < date.today() for po in open_pos)
    earliest = min((po.expected_receipt_date for po in open_pos), default=None)

    projection = project_material_balance(repo, material_id, plant_id)
    covers_shortfall = projection.shortage_date is None

    return PoCoverage(
        material_id=material_id,
        plant_id=plant_id,
        open_po_qty=open_qty,
        earliest_expected_receipt=earliest,
        has_late_po=has_late_po,
        covers_shortfall=covers_shortfall,
    )
