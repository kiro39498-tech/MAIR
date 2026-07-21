"""
Unit tests for the deterministic analytics engine. Run with: pytest tests/
"""
import pandas as pd
import pytest

from data.repository import get_repository
from analytics.health_classification import get_material_health, get_all_material_health
from analytics.inventory_calc import get_usable_inventory
from analytics.bom_explosion import explode_product_qty, products_using_material
from analytics.projection import project_material_balance
from analytics.po_analysis import analyze_po_coverage
from analytics.production_impact import get_production_impact
from analytics.priority_scoring import score_material, rank_at_risk_materials
from analytics.replenishment import recommend_for_material, draft_recommendations


@pytest.fixture(scope="module")
def repo():
    return get_repository()


def test_repository_loads_all_tables(repo):
    assert len(repo.plants) == 3
    assert len(repo.materials) == 500
    assert len(repo.inventory) > 0
    assert len(repo.suppliers) == 100


def test_usable_inventory_is_unrestricted_minus_reserved(repo):
    snap = repo.inventory[0]
    usable = get_usable_inventory(repo, snap.material_id, snap.plant_id)
    assert usable == pytest.approx(snap.unrestricted_qty - snap.reserved_qty)


def test_health_classification_matches_answer_key(repo):
    """The dataset ships a ground-truth answer key. This is the key
    correctness check for the whole engine — see data/csv/data_dictionary.md."""
    answer_key = pd.read_csv("data/csv/_answer_key_inventory_status.csv")
    total, match = 0, 0
    for _, row in answer_key.iterrows():
        health = get_material_health(repo, row["material_id"], row["plant_id"])
        total += 1
        if health and health.status == row["expected_status"]:
            match += 1
    agreement = match / total
    assert agreement > 0.95, f"Health classification agreement too low: {agreement:.1%}"


def test_every_policy_row_produces_a_health_result(repo):
    results = get_all_material_health(repo)
    assert len(results) == len(repo.inventory_policies)
    assert {r.status for r in results} <= {
        "Healthy", "Near Reorder", "Safety Stock Warning", "Shortage", "Excess"
    }


def test_bom_explosion_is_linear_in_quantity(repo):
    product_id = repo.products[0].product_id
    demand_1x = explode_product_qty(repo, product_id, 1)
    demand_10x = explode_product_qty(repo, product_id, 10)
    for material_id, qty in demand_1x.items():
        assert demand_10x[material_id] == pytest.approx(qty * 10)


def test_products_using_material_is_reverse_of_bom(repo):
    material_id = repo.bom[0].material_id
    products = products_using_material(repo, material_id)
    assert repo.bom[0].product_id in products


def test_projection_returns_horizon_plus_one_points(repo):
    mat, plant = repo.inventory[0].material_id, repo.inventory[0].plant_id
    proj = project_material_balance(repo, mat, plant, horizon_days=30)
    assert len(proj.points) == 31
    assert proj.points[0].date > proj.points[0].date - pd.Timedelta(days=1).to_pytimedelta()


def test_shortage_materials_project_a_shortage_or_are_covered(repo):
    shortages = [k for k in repo.policy_by_key if get_material_health(repo, *k).status == "Shortage"]
    assert len(shortages) > 0
    for mat, plant in shortages[:15]:
        proj = project_material_balance(repo, mat, plant)
        coverage = analyze_po_coverage(repo, mat, plant)
        # A shortage-status material should either show a projected
        # shortage date, or already have enough open PO coverage to avoid one.
        assert proj.shortage_date is not None or coverage.covers_shortfall


def test_production_impact_only_counts_open_orders(repo):
    mat, plant = repo.inventory[0].material_id, repo.inventory[0].plant_id
    impact = get_production_impact(repo, mat, plant)
    order_ids = set(impact.affected_production_orders)
    for po in repo.production_orders:
        if po.production_order_id in order_ids:
            assert po.status in ("Released", "In Process", "Confirmed", "Delayed")


def test_priority_score_is_between_0_and_1(repo):
    mat, plant = repo.inventory[0].material_id, repo.inventory[0].plant_id
    score = score_material(repo, mat, plant)
    assert 0.0 <= score <= 1.0


def test_rank_at_risk_materials_sorted_descending(repo):
    ranked = rank_at_risk_materials(repo, top_n=15)
    scores = [r["score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_healthy_material_recommends_monitor(repo):
    healthy = next(k for k in repo.policy_by_key if get_material_health(repo, *k).status == "Healthy")
    rec = recommend_for_material(repo, *healthy)
    assert rec.recommended_action == "Monitor"


def test_shortage_material_never_recommends_monitor_without_coverage(repo):
    shortages = [k for k in repo.policy_by_key if get_material_health(repo, *k).status == "Shortage"]
    for mat, plant in shortages[:15]:
        rec = recommend_for_material(repo, mat, plant)
        coverage = analyze_po_coverage(repo, mat, plant)
        if rec.recommended_action == "Monitor":
            assert coverage.covers_shortfall and not coverage.has_late_po


def test_draft_recommendations_are_draft_only(repo):
    """Phase 1 contract: this module must never place an order. There should
    be no supplier-write/PO-creation side effect anywhere in this call."""
    recs = draft_recommendations(repo, top_n=10)
    assert len(recs) > 0
    for r in recs:
        assert r.recommended_action in (
            "Monitor", "Replenish", "Expedite", "Restore Safety Stock", "Transfer"
        )


def test_replenishment_shortage_reduced_by_po():
    from unittest.mock import patch
    from models.schemas import Material, InventoryPolicy, InventorySnapshot, PurchaseOrder, SupplierMaterial
    from data.repository import Repository
    from analytics.replenishment import recommend_for_material

    # Build mock data.
    # The engine now uses reorder_point_qty from the policy directly (no lead-time re-adjustment).
    # Setup: usable=50, reorder_point=200 (already encodes lead-time), safety_stock=100
    # Shortfall = 200 - 50 = 150.  Open PO = 100.  Net shortfall = 50.
    mock_materials = [Material(material_id="MAT-MOCK-1", material_name="Mock 1", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A")]
    mock_policies = [InventoryPolicy(material_id="MAT-MOCK-1", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=200.0, max_stock_qty=500.0, reorder_qty=10.0)]
    mock_inventory = [InventorySnapshot(material_id="MAT-MOCK-1", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=50.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18")]
    mock_pos = [PurchaseOrder(po_id="PO-1", po_line=1, material_id="MAT-MOCK-1", supplier_id="SUP-1", plant_id="PLT-1", order_qty=100, open_qty=100, unit_price=10.0, order_date="2026-07-10", expected_receipt_date="2026-07-28", status="Open")]
    mock_supplier_mats = [SupplierMaterial(supplier_material_id="SM-1", supplier_id="SUP-1", material_id="MAT-MOCK-1", unit_price=10.0, lead_time_days=10, moq=10, is_primary_supplier=True)]

    with patch('data.repository.get_connector') as mock_get_conn:
        mock_conn = mock_get_conn.return_value
        mock_conn.get_materials.return_value = mock_materials
        mock_conn.get_inventory_policies.return_value = mock_policies
        mock_conn.get_inventory.return_value = mock_inventory
        mock_conn.get_purchase_orders.return_value = mock_pos
        mock_conn.get_supplier_materials.return_value = mock_supplier_mats
        mock_conn.get_plants.return_value = []
        mock_conn.get_warehouses.return_value = []
        mock_conn.get_products.return_value = []
        mock_conn.get_bom.return_value = []
        mock_conn.get_suppliers.return_value = []
        mock_conn.get_demand_forecast.return_value = []
        mock_conn.get_inventory_transactions.return_value = []
        mock_conn.get_managers.return_value = []

        test_repo = Repository()
        # Shortfall=150, open PO=100 → net shortfall=50.
        # max(reorder_qty=10, net_shortfall=50) = 50, rounded to MOQ 10 → recommends 50.
        rec = recommend_for_material(test_repo, "MAT-MOCK-1", "PLT-1")
        assert rec.recommended_action == "Restore Safety Stock"
        assert rec.recommended_qty == 50  # net shortfall 50, already a multiple of MOQ 10


def test_replenishment_moq_rounding():
    from unittest.mock import patch
    from models.schemas import Material, InventoryPolicy, InventorySnapshot, PurchaseOrder, SupplierMaterial
    from data.repository import Repository
    from analytics.replenishment import recommend_for_material

    mock_materials = [Material(material_id="MAT-MOCK-2", material_name="Mock 2", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A")]
    # reorder_point_qty=200 already encodes lead time (10 days * 10 usage + 100 SS).
    # Usable=150 → shortfall=50. No PO. MOQ=100 → rounds up to 100.
    mock_policies = [InventoryPolicy(material_id="MAT-MOCK-2", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=200.0, max_stock_qty=500.0, reorder_qty=10.0)]
    mock_inventory = [InventorySnapshot(material_id="MAT-MOCK-2", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=150.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18")]
    mock_supplier_mats = [SupplierMaterial(supplier_material_id="SM-2", supplier_id="SUP-2", material_id="MAT-MOCK-2", unit_price=10.0, lead_time_days=10, moq=100, is_primary_supplier=True)]

    with patch('data.repository.get_connector') as mock_get_conn:
        mock_conn = mock_get_conn.return_value
        mock_conn.get_materials.return_value = mock_materials
        mock_conn.get_inventory_policies.return_value = mock_policies
        mock_conn.get_inventory.return_value = mock_inventory
        mock_conn.get_purchase_orders.return_value = []
        mock_conn.get_supplier_materials.return_value = mock_supplier_mats
        mock_conn.get_plants.return_value = []
        mock_conn.get_warehouses.return_value = []
        mock_conn.get_products.return_value = []
        mock_conn.get_bom.return_value = []
        mock_conn.get_suppliers.return_value = []
        mock_conn.get_demand_forecast.return_value = []
        mock_conn.get_inventory_transactions.return_value = []
        mock_conn.get_managers.return_value = []

        test_repo = Repository()

        # usable=150, ROP=200 → shortfall=50. net_shortfall=50. MOQ=100 → round up to 100.
        rec = recommend_for_material(test_repo, "MAT-MOCK-2", "PLT-1")
        assert rec.recommended_qty == 100

        # usable=80, ROP=200 → shortfall=120. net_shortfall=120. MOQ=100 → round up to 200.
        test_repo.inventory[0].unrestricted_qty = 80.0
        test_repo._index()
        rec = recommend_for_material(test_repo, "MAT-MOCK-2", "PLT-1")
        assert rec.recommended_qty == 200


def test_replenishment_transfer_preferred():
    from unittest.mock import patch
    from models.schemas import Material, InventoryPolicy, InventorySnapshot, SupplierMaterial
    from data.repository import Repository
    from analytics.replenishment import recommend_for_material

    mock_materials = [Material(material_id="MAT-MOCK-3", material_name="Mock 3", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A")]
    # reorder_point_qty=200 already encodes lead time.
    # PLT-1: usable=50, ROP=200 → shortfall=150. No PO. Transfer from PLT-2.
    # PLT-2: usable=300, SS=100 → surplus=200 ≥ shortfall=150. Donor.
    mock_policies = [
        InventoryPolicy(material_id="MAT-MOCK-3", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=200.0, max_stock_qty=500.0, reorder_qty=10.0),
        InventoryPolicy(material_id="MAT-MOCK-3", plant_id="PLT-2", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=200.0, max_stock_qty=500.0, reorder_qty=10.0),
    ]
    mock_inventory = [
        InventorySnapshot(material_id="MAT-MOCK-3", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=50.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18"),
        InventorySnapshot(material_id="MAT-MOCK-3", plant_id="PLT-2", warehouse_id="WH-2", unrestricted_qty=300.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18"),
    ]
    mock_supplier_mats = [SupplierMaterial(supplier_material_id="SM-3", supplier_id="SUP-3", material_id="MAT-MOCK-3", unit_price=10.0, lead_time_days=10, moq=10, is_primary_supplier=True)]

    with patch('data.repository.get_connector') as mock_get_conn:
        mock_conn = mock_get_conn.return_value
        mock_conn.get_materials.return_value = mock_materials
        mock_conn.get_inventory_policies.return_value = mock_policies
        mock_conn.get_inventory.return_value = mock_inventory
        mock_conn.get_purchase_orders.return_value = []
        mock_conn.get_supplier_materials.return_value = mock_supplier_mats
        mock_conn.get_plants.return_value = []
        mock_conn.get_warehouses.return_value = []
        mock_conn.get_products.return_value = []
        mock_conn.get_bom.return_value = []
        mock_conn.get_suppliers.return_value = []
        mock_conn.get_demand_forecast.return_value = []
        mock_conn.get_inventory_transactions.return_value = []
        mock_conn.get_managers.return_value = []

        test_repo = Repository()

        # Transfer of 150 units from PLT-2 (surplus=200) should be recommended
        rec = recommend_for_material(test_repo, "MAT-MOCK-3", "PLT-1")
        assert rec.recommended_action == "Transfer"
        assert rec.recommended_qty == 150
        assert "PLT-2" in rec.rationale


def test_replenishment_regression_task_a():
    from unittest.mock import patch
    from models.schemas import Material, InventoryPolicy, InventorySnapshot, SupplierMaterial
    from data.repository import Repository
    from analytics.replenishment import recommend_for_material

    mock_materials = [
        Material(material_id="MAT-REG-1", material_name="Reg 1", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A"),
        Material(material_id="MAT-REG-2", material_name="Reg 2", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A"),
        Material(material_id="MAT-REG-3", material_name="Reg 3", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A")
    ]
    mock_policies = [
        InventoryPolicy(material_id="MAT-REG-1", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=200.0),
        InventoryPolicy(material_id="MAT-REG-2", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=300.0),
        InventoryPolicy(material_id="MAT-REG-3", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=400.0)
    ]
    mock_inventory = [
        InventorySnapshot(material_id="MAT-REG-1", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=50.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18"),
        InventorySnapshot(material_id="MAT-REG-2", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=50.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18"),
        InventorySnapshot(material_id="MAT-REG-3", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=50.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18")
    ]
    mock_supplier_mats = [
        SupplierMaterial(supplier_material_id="SM-1", supplier_id="SUP-REG-1", material_id="MAT-REG-1", unit_price=10.0, lead_time_days=10, moq=100, is_primary_supplier=True),
        SupplierMaterial(supplier_material_id="SM-2", supplier_id="SUP-REG-2", material_id="MAT-REG-2", unit_price=10.0, lead_time_days=10, moq=150, is_primary_supplier=True),
        SupplierMaterial(supplier_material_id="SM-3", supplier_id="SUP-REG-3", material_id="MAT-REG-3", unit_price=10.0, lead_time_days=10, moq=500, is_primary_supplier=True)
    ]

    with patch('data.repository.get_connector') as mock_get_conn:
        mock_conn = mock_get_conn.return_value
        mock_conn.get_materials.return_value = mock_materials
        mock_conn.get_inventory_policies.return_value = mock_policies
        mock_conn.get_inventory.return_value = mock_inventory
        mock_conn.get_purchase_orders.return_value = []
        mock_conn.get_supplier_materials.return_value = mock_supplier_mats
        mock_conn.get_plants.return_value = []
        mock_conn.get_warehouses.return_value = []
        mock_conn.get_products.return_value = []
        mock_conn.get_bom.return_value = []
        mock_conn.get_suppliers.return_value = []
        mock_conn.get_demand_forecast.return_value = []
        mock_conn.get_inventory_transactions.return_value = []
        mock_conn.get_managers.return_value = []

        test_repo = Repository()
        
        rec1 = recommend_for_material(test_repo, "MAT-REG-1", "PLT-1")
        rec2 = recommend_for_material(test_repo, "MAT-REG-2", "PLT-1")
        rec3 = recommend_for_material(test_repo, "MAT-REG-3", "PLT-1")
        
        assert rec1.suggested_supplier_id == "SUP-REG-1"
        assert rec2.suggested_supplier_id == "SUP-REG-2"
        assert rec3.suggested_supplier_id == "SUP-REG-3"
        
        assert rec1.recommended_qty == 200
        assert rec2.recommended_qty == 300
        assert rec3.recommended_qty == 500


def test_product_bom_risk_rollups():
    from unittest.mock import patch
    from models.schemas import Material, InventoryPolicy, InventorySnapshot, Product, BomLine
    from data.repository import Repository
    from analytics.product_bom_risk import get_product_risk

    mock_materials = [
        Material(material_id="MAT-BOM-1", material_name="Comp 1", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A"),
        Material(material_id="MAT-BOM-2", material_name="Comp 2", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A"),
    ]
    mock_products = [
        Product(
            product_id="PROD-BOM-1",
            product_name="Fin Good 1",
            family_id="F1",
            primary_plant_id="PLT-1",
            unit_of_measure="EA",
            standard_cost=100.0,
            lifecycle_status="Active"
        )
    ]
    from datetime import date
    mock_bom = [
        BomLine(bom_id="B1", product_id="PROD-BOM-1", material_id="MAT-BOM-1", quantity_per_unit=1.0, bom_version="V1", effective_date=date(2026, 1, 1)),
        BomLine(bom_id="B2", product_id="PROD-BOM-1", material_id="MAT-BOM-2", quantity_per_unit=2.0, bom_version="V1", effective_date=date(2026, 1, 1))
    ]
    mock_policies = [
        InventoryPolicy(material_id="MAT-BOM-1", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=100.0),
        InventoryPolicy(material_id="MAT-BOM-2", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=100.0)
    ]
    mock_inventory = [
        InventorySnapshot(material_id="MAT-BOM-1", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=50.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18"),
        InventorySnapshot(material_id="MAT-BOM-2", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=300.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18")
    ]
    from models.schemas import SupplierMaterial
    mock_supplier_mats = [
        SupplierMaterial(supplier_material_id="SM-B1", supplier_id="SUP-B1", material_id="MAT-BOM-1", unit_price=10.0, lead_time_days=5, moq=10, is_primary_supplier=True),
        SupplierMaterial(supplier_material_id="SM-B2", supplier_id="SUP-B2", material_id="MAT-BOM-2", unit_price=10.0, lead_time_days=5, moq=10, is_primary_supplier=True)
    ]

    with patch('data.repository.get_connector') as mock_get_conn:
        mock_conn = mock_get_conn.return_value
        mock_conn.get_materials.return_value = mock_materials
        mock_conn.get_products.return_value = mock_products
        mock_conn.get_bom.return_value = mock_bom
        mock_conn.get_inventory_policies.return_value = mock_policies
        mock_conn.get_inventory.return_value = mock_inventory
        mock_conn.get_plants.return_value = []
        mock_conn.get_warehouses.return_value = []
        mock_conn.get_suppliers.return_value = []
        mock_conn.get_supplier_materials.return_value = mock_supplier_mats
        mock_conn.get_purchase_orders.return_value = []
        mock_conn.get_demand_forecast.return_value = []
        mock_conn.get_inventory_transactions.return_value = []
        mock_conn.get_managers.return_value = []

        test_repo = Repository()

        # Scenario 1: One component is Safety Stock Warning, one is Healthy -> Product is Safety Stock Warning
        risk1 = get_product_risk(test_repo, "PROD-BOM-1", "PLT-1")
        assert risk1.risk_status == "Safety Stock Warning"
        assert len(risk1.blocking_components) == 1
        assert risk1.blocking_components[0].material_id == "MAT-BOM-1"

        # Scenario 2: Make component 1 a Shortage (Usable = 5.0) -> Product is Shortage
        test_repo.inventory[0].unrestricted_qty = 5.0
        test_repo._index()
        risk2 = get_product_risk(test_repo, "PROD-BOM-1", "PLT-1")
        assert risk2.risk_status == "Shortage"
        assert len(risk2.blocking_components) == 1
        assert risk2.blocking_components[0].material_id == "MAT-BOM-1"

        # Scenario 3: Make component 1 Near Reorder (Usable = 140.0) -> Product is Near Reorder
        test_repo.inventory[0].unrestricted_qty = 140.0
        test_repo._index()
        risk3 = get_product_risk(test_repo, "PROD-BOM-1", "PLT-1")
        assert risk3.risk_status == "Near Reorder"

        # Scenario 4: Make both Healthy (Usable = 300.0) -> Product is Healthy
        test_repo.inventory[0].unrestricted_qty = 300.0
        test_repo._index()
        risk4 = get_product_risk(test_repo, "PROD-BOM-1", "PLT-1")
        assert risk4.risk_status == "Healthy"
        assert len(risk4.blocking_components) == 0


def test_get_products_for_material():
    from unittest.mock import patch
    from models.schemas import Material, InventoryPolicy, InventorySnapshot, Product, BomLine, SupplierMaterial
    from data.repository import Repository
    from analytics.product_bom_risk import get_products_for_material

    mock_materials = [
        Material(material_id="MAT-SHARED-1", material_name="Shared Component", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A")
    ]
    mock_products = [
        Product(product_id="PROD-1", product_name="Fin Good 1", family_id="F1", primary_plant_id="PLT-1", unit_of_measure="EA", standard_cost=100.0, lifecycle_status="Active"),
        Product(product_id="PROD-2", product_name="Fin Good 2", family_id="F1", primary_plant_id="PLT-2", unit_of_measure="EA", standard_cost=120.0, lifecycle_status="Active"),
        Product(product_id="PROD-3", product_name="Fin Good 3", family_id="F1", primary_plant_id="PLT-3", unit_of_measure="EA", standard_cost=150.0, lifecycle_status="Active")
    ]
    from datetime import date
    mock_bom = [
        BomLine(bom_id="B1", product_id="PROD-1", material_id="MAT-SHARED-1", quantity_per_unit=1.0, bom_version="V1", effective_date=date(2026, 1, 1)),
        BomLine(bom_id="B2", product_id="PROD-2", material_id="MAT-SHARED-1", quantity_per_unit=2.0, bom_version="V1", effective_date=date(2026, 1, 1)),
        BomLine(bom_id="B3", product_id="PROD-3", material_id="MAT-SHARED-1", quantity_per_unit=3.0, bom_version="V1", effective_date=date(2026, 1, 1))
    ]
    mock_policies = [
        InventoryPolicy(material_id="MAT-SHARED-1", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=100.0),
        InventoryPolicy(material_id="MAT-SHARED-1", plant_id="PLT-2", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=100.0),
        InventoryPolicy(material_id="MAT-SHARED-1", plant_id="PLT-3", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=100.0)
    ]
    mock_inventory = [
        # PLT-1 has shortage (Usable = 5.0 < Reorder Point = 150)
        InventorySnapshot(material_id="MAT-SHARED-1", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=5.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18"),
        # PLT-2 is healthy (Usable = 300.0 > Reorder Point = 150)
        InventorySnapshot(material_id="MAT-SHARED-1", plant_id="PLT-2", warehouse_id="WH-1", unrestricted_qty=300.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18"),
        # PLT-3 is healthy (Usable = 400.0 > Reorder Point = 150)
        InventorySnapshot(material_id="MAT-SHARED-1", plant_id="PLT-3", warehouse_id="WH-1", unrestricted_qty=400.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18")
    ]
    mock_supplier_mats = [
        SupplierMaterial(supplier_material_id="SM-1", supplier_id="SUP-1", material_id="MAT-SHARED-1", unit_price=10.0, lead_time_days=5, moq=10, is_primary_supplier=True)
    ]
    from models.schemas import Plant
    mock_plants = [
        Plant(plant_id="PLT-1", plant_name="Plant 1", country="US", region="NA", plant_type="Assembly", timezone="EST"),
        Plant(plant_id="PLT-2", plant_name="Plant 2", country="US", region="NA", plant_type="Assembly", timezone="EST"),
        Plant(plant_id="PLT-3", plant_name="Plant 3", country="US", region="NA", plant_type="Assembly", timezone="EST")
    ]

    with patch('data.repository.get_connector') as mock_get_conn:
        mock_conn = mock_get_conn.return_value
        mock_conn.get_materials.return_value = mock_materials
        mock_conn.get_products.return_value = mock_products
        mock_conn.get_bom.return_value = mock_bom
        mock_conn.get_inventory_policies.return_value = mock_policies
        mock_conn.get_inventory.return_value = mock_inventory
        mock_conn.get_plants.return_value = mock_plants
        mock_conn.get_warehouses.return_value = []
        mock_conn.get_suppliers.return_value = []
        mock_conn.get_supplier_materials.return_value = mock_supplier_mats
        mock_conn.get_purchase_orders.return_value = []
        mock_conn.get_demand_forecast.return_value = []
        mock_conn.get_inventory_transactions.return_value = []
        mock_conn.get_managers.return_value = []

        test_repo = Repository()

        # 1. Verify query with no plant filter (returns all plants where product is present)
        # Each product-plant row should be returned.
        # Since PROD-1, PROD-2, PROD-3 are evaluated across all plants, let's see how many rows are returned.
        # Note: get_product_risk loops over the product's primary plant, or rather, get_products_for_material
        # checks all plants in test_repo.plants.
        results = get_products_for_material(test_repo, "MAT-SHARED-1")
        
        # PROD-1, PROD-2, PROD-3 evaluated at PLT-1, PLT-2, PLT-3.
        # Total combinations: 3 products * 3 plants = 9 rows.
        # For PLT-1 combinations, since MAT-SHARED-1 is in shortage at PLT-1, is_blocking should be True.
        # For PLT-2 and PLT-3 combinations, since MAT-SHARED-1 is healthy, is_blocking should be False.
        assert len(results) == 9
        
        # Verify specific is_blocking status
        plt1_rows = [r for r in results if r.plant_id == "PLT-1"]
        assert len(plt1_rows) == 3
        for r in plt1_rows:
            assert r.is_blocking is True
            assert r.risk_status == "Shortage"

        plt2_rows = [r for r in results if r.plant_id == "PLT-2"]
        assert len(plt2_rows) == 3
        for r in plt2_rows:
            assert r.is_blocking is False
            assert r.risk_status == "Healthy"

        # 2. Verify query with plant filter PLT-1
        results_plt1 = get_products_for_material(test_repo, "MAT-SHARED-1", plant_id="PLT-1")
        assert len(results_plt1) == 3
        assert all(r.plant_id == "PLT-1" for r in results_plt1)
        assert all(r.is_blocking is True for r in results_plt1)

        # 3. Verify query for non-existent material
        results_empty = get_products_for_material(test_repo, "MAT-NON-EXISTENT")
        assert results_empty == []





# ---------------------------------------------------------------------------
# Tests for Tasks 1-3 (BOM completeness, plant-invariant BOM, MAT-00158)
# ---------------------------------------------------------------------------

class TestProductBomRiskCompleteness:
    """Task 1 — every product×plant combination must appear; no hardcoded status filter."""

    def test_endpoint_applies_no_default_status_filter(self, repo):
        """The analytics layer must not silently drop any status.
        All returned statuses must be valid, and if all rows share the same
        status it must be because that is genuinely what the data says — not
        because a filter is hiding other rows.

        We verify this by checking that:
        (a) every call to get_product_risk that returns a row uses the full
            BOM (all_components contains ≥ 1 entry), and
        (b) the total row count equals the number of product×plant pairs that
            actually have BOM lines — no rows are dropped by a status filter.
        """
        from analytics.product_bom_risk import get_product_risk

        valid_statuses = {"Healthy", "Near Reorder", "Safety Stock Warning", "Shortage", "Excess"}
        expected_rows = 0
        returned_rows = 0

        for product in repo.products:
            for plant in repo.plants:
                # A row is expected when the product has BOM lines
                has_bom = bool(repo.bom_by_product.get(product.product_id))
                row = get_product_risk(repo, product.product_id, plant.plant_id)

                if has_bom:
                    expected_rows += 1
                    assert row is not None, (
                        f"Expected a row for {product.product_id} @ {plant.plant_id} "
                        f"(it has BOM lines) but got None"
                    )
                    assert row.risk_status in valid_statuses, (
                        f"Unexpected status '{row.risk_status}' for {product.product_id} @ {plant.plant_id}"
                    )
                    assert len(row.all_components) > 0, (
                        f"all_components is empty for {product.product_id} @ {plant.plant_id}"
                    )
                    returned_rows += 1
                else:
                    # Products with no BOM legitimately return None
                    assert row is None

        assert returned_rows == expected_rows, (
            f"Row count mismatch: expected {expected_rows}, got {returned_rows}"
        )

    def test_get_product_risk_returns_healthy_products(self):
        """A product whose every component is Healthy must return risk_status='Healthy',
        not None — i.e. the function does not silently drop healthy rows."""
        from unittest.mock import patch
        from datetime import date
        from models.schemas import (
            Material, InventoryPolicy, InventorySnapshot, Product, BomLine, SupplierMaterial
        )
        from data.repository import Repository
        from analytics.product_bom_risk import get_product_risk

        mock_materials = [
            Material(material_id="MAT-H-1", material_name="H1", material_type="RAW",
                     unit_of_measure="PC", standard_cost=1.0, criticality="Low", abc_class="C"),
        ]
        mock_products = [
            Product(product_id="PROD-H-1", product_name="Healthy Prod", family_id="F1",
                    primary_plant_id="PLT-1", unit_of_measure="EA",
                    standard_cost=10.0, lifecycle_status="Active"),
        ]
        mock_bom = [
            BomLine(bom_id="BH1", product_id="PROD-H-1", material_id="MAT-H-1",
                    quantity_per_unit=1.0, bom_version="V1", effective_date=date(2026, 1, 1)),
        ]
        # Usable = 500 >> reorder_point = 100 → status Healthy
        mock_policies = [
            InventoryPolicy(material_id="MAT-H-1", plant_id="PLT-1",
                            avg_daily_usage=5.0, safety_stock_qty=50.0,
                            reorder_point_qty=100.0, max_stock_qty=600.0, reorder_qty=100.0),
        ]
        mock_inventory = [
            InventorySnapshot(material_id="MAT-H-1", plant_id="PLT-1", warehouse_id="WH-1",
                              unrestricted_qty=500.0, quality_hold_qty=0.0,
                              blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-21"),
        ]
        mock_supplier = [
            SupplierMaterial(supplier_material_id="SM-H1", supplier_id="SUP-H1",
                             material_id="MAT-H-1", unit_price=1.0, lead_time_days=7,
                             moq=10, is_primary_supplier=True),
        ]
        with patch("data.repository.get_connector") as mock_gc:
            c = mock_gc.return_value
            c.get_materials.return_value = mock_materials
            c.get_products.return_value = mock_products
            c.get_bom.return_value = mock_bom
            c.get_inventory_policies.return_value = mock_policies
            c.get_inventory.return_value = mock_inventory
            c.get_supplier_materials.return_value = mock_supplier
            for attr in ("get_plants", "get_warehouses", "get_suppliers",
                         "get_purchase_orders", "get_demand_forecast",
                         "get_inventory_transactions", "get_managers"):
                getattr(c, attr).return_value = []
            r = Repository()
            row = get_product_risk(r, "PROD-H-1", "PLT-1")
            assert row is not None, "get_product_risk returned None for a healthy product"
            assert row.risk_status == "Healthy"
            assert len(row.blocking_components) == 0
        """A product whose every component is Healthy must return risk_status='Healthy',
        not None — i.e. the function does not silently drop healthy rows."""
        from unittest.mock import patch
        from datetime import date
        from models.schemas import (
            Material, InventoryPolicy, InventorySnapshot, Product, BomLine, SupplierMaterial
        )
        from data.repository import Repository
        from analytics.product_bom_risk import get_product_risk

        mock_materials = [
            Material(material_id="MAT-H-1", material_name="H1", material_type="RAW",
                     unit_of_measure="PC", standard_cost=1.0, criticality="Low", abc_class="C"),
        ]
        mock_products = [
            Product(product_id="PROD-H-1", product_name="Healthy Prod", family_id="F1",
                    primary_plant_id="PLT-1", unit_of_measure="EA",
                    standard_cost=10.0, lifecycle_status="Active"),
        ]
        mock_bom = [
            BomLine(bom_id="BH1", product_id="PROD-H-1", material_id="MAT-H-1",
                    quantity_per_unit=1.0, bom_version="V1", effective_date=date(2026, 1, 1)),
        ]
        # Usable = 500 >> reorder_point = 100 → status Healthy
        mock_policies = [
            InventoryPolicy(material_id="MAT-H-1", plant_id="PLT-1",
                            avg_daily_usage=5.0, safety_stock_qty=50.0,
                            reorder_point_qty=100.0, max_stock_qty=600.0, reorder_qty=100.0),
        ]
        mock_inventory = [
            InventorySnapshot(material_id="MAT-H-1", plant_id="PLT-1", warehouse_id="WH-1",
                              unrestricted_qty=500.0, quality_hold_qty=0.0,
                              blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-21"),
        ]
        mock_supplier = [
            SupplierMaterial(supplier_material_id="SM-H1", supplier_id="SUP-H1",
                             material_id="MAT-H-1", unit_price=1.0, lead_time_days=7,
                             moq=10, is_primary_supplier=True),
        ]
        with patch("data.repository.get_connector") as mock_gc:
            c = mock_gc.return_value
            c.get_materials.return_value = mock_materials
            c.get_products.return_value = mock_products
            c.get_bom.return_value = mock_bom
            c.get_inventory_policies.return_value = mock_policies
            c.get_inventory.return_value = mock_inventory
            c.get_supplier_materials.return_value = mock_supplier
            for attr in ("get_plants", "get_warehouses", "get_suppliers",
                         "get_purchase_orders", "get_demand_forecast",
                         "get_inventory_transactions", "get_managers"):
                getattr(c, attr).return_value = []
            r = Repository()
            row = get_product_risk(r, "PROD-H-1", "PLT-1")
            assert row is not None, "get_product_risk returned None for a healthy product"
            assert row.risk_status == "Healthy"
            assert len(row.blocking_components) == 0


class TestFullBomComponentList:
    """Task 2 — the full BOM component list must include every component, all statuses."""

    def test_all_components_includes_healthy_and_excess(self):
        """all_components must contain every BOM line, not just blockers."""
        from unittest.mock import patch
        from datetime import date
        from models.schemas import (
            Material, InventoryPolicy, InventorySnapshot, Product, BomLine, SupplierMaterial
        )
        from data.repository import Repository
        from analytics.product_bom_risk import get_product_risk

        mock_materials = [
            Material(material_id="MAT-MIX-1", material_name="Shortage Comp", material_type="RAW",
                     unit_of_measure="PC", standard_cost=1.0, criticality="High", abc_class="A"),
            Material(material_id="MAT-MIX-2", material_name="Healthy Comp", material_type="RAW",
                     unit_of_measure="PC", standard_cost=1.0, criticality="Low", abc_class="C"),
            Material(material_id="MAT-MIX-3", material_name="Excess Comp", material_type="RAW",
                     unit_of_measure="PC", standard_cost=1.0, criticality="Low", abc_class="C"),
        ]
        mock_products = [
            Product(product_id="PROD-MIX-1", product_name="Mixed BOM Prod", family_id="F1",
                    primary_plant_id="PLT-1", unit_of_measure="EA",
                    standard_cost=100.0, lifecycle_status="Active"),
        ]
        mock_bom = [
            BomLine(bom_id="BM1", product_id="PROD-MIX-1", material_id="MAT-MIX-1",
                    quantity_per_unit=1.0, bom_version="V1", effective_date=date(2026, 1, 1)),
            BomLine(bom_id="BM2", product_id="PROD-MIX-1", material_id="MAT-MIX-2",
                    quantity_per_unit=2.0, bom_version="V1", effective_date=date(2026, 1, 1)),
            BomLine(bom_id="BM3", product_id="PROD-MIX-1", material_id="MAT-MIX-3",
                    quantity_per_unit=3.0, bom_version="V1", effective_date=date(2026, 1, 1)),
        ]
        mock_policies = [
            # MAT-MIX-1: shortage (usable=5 < reorder=100)
            InventoryPolicy(material_id="MAT-MIX-1", plant_id="PLT-1",
                            avg_daily_usage=5.0, safety_stock_qty=50.0,
                            reorder_point_qty=100.0, max_stock_qty=500.0, reorder_qty=100.0),
            # MAT-MIX-2: healthy (usable=300 > reorder=100)
            InventoryPolicy(material_id="MAT-MIX-2", plant_id="PLT-1",
                            avg_daily_usage=5.0, safety_stock_qty=50.0,
                            reorder_point_qty=100.0, max_stock_qty=500.0, reorder_qty=100.0),
            # MAT-MIX-3: excess (usable=600 > max=500)
            InventoryPolicy(material_id="MAT-MIX-3", plant_id="PLT-1",
                            avg_daily_usage=5.0, safety_stock_qty=50.0,
                            reorder_point_qty=100.0, max_stock_qty=500.0, reorder_qty=100.0),
        ]
        mock_inventory = [
            InventorySnapshot(material_id="MAT-MIX-1", plant_id="PLT-1", warehouse_id="WH-1",
                              unrestricted_qty=5.0, quality_hold_qty=0.0,
                              blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-21"),
            InventorySnapshot(material_id="MAT-MIX-2", plant_id="PLT-1", warehouse_id="WH-1",
                              unrestricted_qty=300.0, quality_hold_qty=0.0,
                              blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-21"),
            InventorySnapshot(material_id="MAT-MIX-3", plant_id="PLT-1", warehouse_id="WH-1",
                              unrestricted_qty=600.0, quality_hold_qty=0.0,
                              blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-21"),
        ]
        mock_supplier = [
            SupplierMaterial(supplier_material_id="SM-MX1", supplier_id="SUP-MX1",
                             material_id="MAT-MIX-1", unit_price=1.0, lead_time_days=7,
                             moq=10, is_primary_supplier=True),
        ]
        with patch("data.repository.get_connector") as mock_gc:
            c = mock_gc.return_value
            c.get_materials.return_value = mock_materials
            c.get_products.return_value = mock_products
            c.get_bom.return_value = mock_bom
            c.get_inventory_policies.return_value = mock_policies
            c.get_inventory.return_value = mock_inventory
            c.get_supplier_materials.return_value = mock_supplier
            for attr in ("get_plants", "get_warehouses", "get_suppliers",
                         "get_purchase_orders", "get_demand_forecast",
                         "get_inventory_transactions", "get_managers"):
                getattr(c, attr).return_value = []
            r = Repository()
            row = get_product_risk(r, "PROD-MIX-1", "PLT-1")
            assert row is not None

            comp_ids = {c.material_id for c in row.all_components}
            assert "MAT-MIX-1" in comp_ids, "Blocking (Shortage) component missing from all_components"
            assert "MAT-MIX-2" in comp_ids, "Healthy component missing from all_components"
            assert "MAT-MIX-3" in comp_ids, "Excess component missing from all_components"
            assert len(row.all_components) == 3

            # Healthy/Excess have net_shortfall == 0
            for comp in row.all_components:
                if comp.health_status in ("Healthy", "Excess"):
                    assert comp.net_shortfall == 0.0, (
                        f"{comp.material_id} is {comp.health_status} but has net_shortfall={comp.net_shortfall}"
                    )
                if comp.health_status == "Shortage":
                    assert comp.net_shortfall > 0.0

            # Blocking components (legacy field) only contains the shortage one
            assert len(row.blocking_components) == 1
            assert row.blocking_components[0].material_id == "MAT-MIX-1"

    def test_all_components_contains_no_data_entry_when_no_policy_at_plant(self):
        """A BOM component without an inventory policy at this plant must appear
        with has_inventory_data=False rather than being silently dropped."""
        from unittest.mock import patch
        from datetime import date
        from models.schemas import (
            Material, InventoryPolicy, InventorySnapshot, Product, BomLine, SupplierMaterial
        )
        from data.repository import Repository
        from analytics.product_bom_risk import get_product_risk

        mock_materials = [
            Material(material_id="MAT-ND-1", material_name="No Data Mat", material_type="RAW",
                     unit_of_measure="PC", standard_cost=1.0, criticality="High", abc_class="A"),
            Material(material_id="MAT-ND-2", material_name="Has Data Mat", material_type="RAW",
                     unit_of_measure="PC", standard_cost=1.0, criticality="Low", abc_class="C"),
        ]
        mock_products = [
            Product(product_id="PROD-ND-1", product_name="No Data Prod", family_id="F1",
                    primary_plant_id="PLT-1", unit_of_measure="EA",
                    standard_cost=10.0, lifecycle_status="Active"),
        ]
        mock_bom = [
            BomLine(bom_id="BND1", product_id="PROD-ND-1", material_id="MAT-ND-1",
                    quantity_per_unit=1.0, bom_version="V1", effective_date=date(2026, 1, 1)),
            BomLine(bom_id="BND2", product_id="PROD-ND-1", material_id="MAT-ND-2",
                    quantity_per_unit=2.0, bom_version="V1", effective_date=date(2026, 1, 1)),
        ]
        # Only MAT-ND-2 has a policy at PLT-1; MAT-ND-1 does not
        mock_policies = [
            InventoryPolicy(material_id="MAT-ND-2", plant_id="PLT-1",
                            avg_daily_usage=5.0, safety_stock_qty=50.0,
                            reorder_point_qty=100.0, max_stock_qty=500.0, reorder_qty=100.0),
        ]
        mock_inventory = [
            InventorySnapshot(material_id="MAT-ND-2", plant_id="PLT-1", warehouse_id="WH-1",
                              unrestricted_qty=300.0, quality_hold_qty=0.0,
                              blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-21"),
        ]
        with patch("data.repository.get_connector") as mock_gc:
            c = mock_gc.return_value
            c.get_materials.return_value = mock_materials
            c.get_products.return_value = mock_products
            c.get_bom.return_value = mock_bom
            c.get_inventory_policies.return_value = mock_policies
            c.get_inventory.return_value = mock_inventory
            c.get_supplier_materials.return_value = []
            for attr in ("get_plants", "get_warehouses", "get_suppliers",
                         "get_purchase_orders", "get_demand_forecast",
                         "get_inventory_transactions", "get_managers"):
                getattr(c, attr).return_value = []
            r = Repository()
            row = get_product_risk(r, "PROD-ND-1", "PLT-1")
            assert row is not None
            assert len(row.all_components) == 2

            no_data = next(c for c in row.all_components if c.material_id == "MAT-ND-1")
            assert no_data.has_inventory_data is False
            assert no_data.health_status == "No Data"


class TestBomPlantInvariance:
    """Task 3 — the BOM recipe (component set) must be identical across all plants.

    FINDING: bom.csv has no plant_id column.  bom_by_product is keyed by
    product_id only.  The BOM recipe IS plant-invariant in this dataset.

    The apparent per-plant variation reported for PROD-0004 was caused by
    components (e.g. MAT-00158) that have inventory policy/snapshot data only
    at a subset of plants.  get_product_risk previously silently skipped those
    components when health data was missing; now it includes them as "No Data"
    entries.  The component set returned in all_components is therefore always
    the same set of material IDs for every plant — only the health statuses vary.

    These tests lock in that invariant.
    """

    def test_bom_csv_has_no_plant_id_column(self, repo):
        """The canonical BomLine schema must not carry plant_id — the recipe is global."""
        from models.schemas import BomLine
        sample = repo.bom[0]
        assert not hasattr(sample, "plant_id"), (
            "BomLine unexpectedly gained a plant_id field — BOM is supposed to be plant-agnostic"
        )

    def test_component_set_identical_across_plants(self, repo):
        """For every product produced at more than one plant, the set of material IDs
        in its BOM must be the same regardless of which plant we query."""
        from analytics.product_bom_risk import get_product_risk

        for product in repo.products:
            plant_component_sets: dict[str, set[str]] = {}
            for plant in repo.plants:
                row = get_product_risk(repo, product.product_id, plant.plant_id)
                if row:
                    plant_component_sets[plant.plant_id] = {
                        c.material_id for c in row.all_components
                    }

            if len(plant_component_sets) < 2:
                continue  # only one plant has data for this product — nothing to compare

            component_sets = list(plant_component_sets.values())
            first = component_sets[0]
            for plant_id, comp_set in plant_component_sets.items():
                assert comp_set == first, (
                    f"Product {product.product_id}: component set at {plant_id} "
                    f"differs from first plant.\n"
                    f"  Only in first: {first - comp_set}\n"
                    f"  Only in {plant_id}: {comp_set - first}"
                )

    def test_mat_00158_appears_in_prod_0004_all_components_at_every_plant(self, repo):
        """MAT-00158 is in PROD-0004's BOM (bom.csv row BOM-00073).
        It must appear in all_components for every plant, even plants where it
        has no inventory policy (those entries get has_inventory_data=False)."""
        from analytics.product_bom_risk import get_product_risk

        for plant in repo.plants:
            row = get_product_risk(repo, "PROD-0004", plant.plant_id)
            assert row is not None, f"get_product_risk returned None for PROD-0004 @ {plant.plant_id}"
            mat_ids = {c.material_id for c in row.all_components}
            assert "MAT-00158" in mat_ids, (
                f"MAT-00158 missing from PROD-0004 all_components @ {plant.plant_id}"
            )

    def test_mat_00158_healthy_at_plt_in_03_absent_from_blockers(self, repo):
        """At PLT-IN-03, MAT-00158 has inventory data and should be Healthy (or
        similar non-blocking status) — it must NOT appear in blocking_components."""
        from analytics.product_bom_risk import get_product_risk

        row = get_product_risk(repo, "PROD-0004", "PLT-IN-03")
        assert row is not None

        # Confirm MAT-00158 is in all_components
        comp = next((c for c in row.all_components if c.material_id == "MAT-00158"), None)
        assert comp is not None, "MAT-00158 not in all_components at PLT-IN-03"
        assert comp.has_inventory_data is True, "MAT-00158 should have inventory data at PLT-IN-03"

        # Since it is Healthy/Excess, it must not be a blocker
        blocker_ids = {bc.material_id for bc in row.blocking_components}
        assert "MAT-00158" not in blocker_ids, (
            f"MAT-00158 is {comp.health_status} but incorrectly appears in blocking_components"
        )

    def test_material_usage_round_trip(self, repo):
        """For any product P and material M in its BOM:
        M must appear in P's all_components, AND
        P must appear in M's material-usage list, with matching qty_per_unit."""
        from analytics.product_bom_risk import get_product_risk, get_products_for_material

        # Sample a few products to keep test runtime reasonable
        sample_products = repo.products[:5]
        first_plant = repo.plants[0].plant_id

        for product in sample_products:
            row = get_product_risk(repo, product.product_id, first_plant)
            if not row:
                continue
            for comp in row.all_components:
                usage_rows = get_products_for_material(repo, comp.material_id, plant_id=first_plant)
                usage_product_ids = {u.product_id for u in usage_rows}
                assert product.product_id in usage_product_ids, (
                    f"Product {product.product_id} has material {comp.material_id} in its BOM, "
                    f"but {comp.material_id}'s material-usage list does not include {product.product_id}"
                )
                # qty_per_unit must match
                usage_row = next(u for u in usage_rows if u.product_id == product.product_id)
                assert usage_row.qty_per_unit == pytest.approx(comp.qty_per_unit), (
                    f"qty_per_unit mismatch for {product.product_id}/{comp.material_id}: "
                    f"BOM={comp.qty_per_unit}, usage={usage_row.qty_per_unit}"
                )
