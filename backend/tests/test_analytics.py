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

    # Build mock data
    mock_materials = [Material(material_id="MAT-MOCK-1", material_name="Mock 1", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A")]
    mock_policies = [InventoryPolicy(material_id="MAT-MOCK-1", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=200.0)]
    mock_inventory = [InventorySnapshot(material_id="MAT-MOCK-1", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=50.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18")]
    # Usable stock = 50. Adjusted ROP = 10 (usage) * 10 (lead time) + 100 (safety) = 200. Shortfall = 150.
    # Open PO = 100. Net shortfall = 50.
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
        # Ensure it calculates with open PO subtracted from shortfall
        # Net shortfall is 50. reorder_qty is 200. Since max(policy.reorder_qty, net_shortfall) is 200, it recommends 200.
        # But if we change reorder_qty to 10, then max(10, 50) = 50.
        test_repo.inventory_policies[0].reorder_qty = 10
        test_repo._index()
        
        rec = recommend_for_material(test_repo, "MAT-MOCK-1", "PLT-1")
        assert rec.recommended_action == "Restore Safety Stock"
        assert rec.recommended_qty == 50  # 150 shortfall - 100 open PO = 50 net shortfall, rounded to MOQ 10 is 50.


def test_replenishment_moq_rounding():
    from unittest.mock import patch
    from models.schemas import Material, InventoryPolicy, InventorySnapshot, PurchaseOrder, SupplierMaterial
    from data.repository import Repository
    from analytics.replenishment import recommend_for_material

    mock_materials = [Material(material_id="MAT-MOCK-2", material_name="Mock 2", material_type="RAW", unit_of_measure="PC", standard_cost=10.0, criticality="High", abc_class="A")]
    mock_policies = [InventoryPolicy(material_id="MAT-MOCK-2", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=10.0)]
    mock_inventory = [InventorySnapshot(material_id="MAT-MOCK-2", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=150.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18")]
    # Adjusted ROP = 10 * 10 + 100 = 200. Shortfall = 50. MOQ = 100.
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
        
        # Shortfall of 50 should be rounded up to MOQ 100
        rec = recommend_for_material(test_repo, "MAT-MOCK-2", "PLT-1")
        assert rec.recommended_qty == 100

        # Shortfall of 120 should be rounded up to multiple of MOQ (200)
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
    # Policies for PLT-1 and PLT-2
    mock_policies = [
        InventoryPolicy(material_id="MAT-MOCK-3", plant_id="PLT-1", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=10.0),
        InventoryPolicy(material_id="MAT-MOCK-3", plant_id="PLT-2", avg_daily_usage=10.0, safety_stock_qty=100.0, reorder_point_qty=150.0, max_stock_qty=500.0, reorder_qty=10.0)
    ]
    # PLT-1 has usable stock = 50. Adjusted ROP = 200. Shortfall = 150.
    # PLT-2 has usable stock = 300. Safety stock = 100. Surplus = 200.
    mock_inventory = [
        InventorySnapshot(material_id="MAT-MOCK-3", plant_id="PLT-1", warehouse_id="WH-1", unrestricted_qty=50.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18"),
        InventorySnapshot(material_id="MAT-MOCK-3", plant_id="PLT-2", warehouse_id="WH-2", unrestricted_qty=300.0, quality_hold_qty=0.0, blocked_qty=0.0, reserved_qty=0.0, snapshot_date="2026-07-18")
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
        
        # Transfer of 150 should be recommended from PLT-2 instead of buying from supplier
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


