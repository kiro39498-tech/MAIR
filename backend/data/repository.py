"""
Master In-Memory Repository Facade (SSOT Section 7, Repository Pattern).

Composes specialized domain repositories (InventoryRepository, BomRepository,
SupplierRepository, ProductionRepository, PurchaseRepository).

This is the ONLY place analytics code reads data from. Data is fetched via
ConnectorFactory.create(settings.DATA_SOURCE). Analytics, MCP tools, agents,
and REST APIs never interact with connectors directly.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Dict, Tuple

from connectors.connector_factory import ConnectorFactory
from connectors.csv_connector import get_connector
from connectors.base import BaseConnector
from models.canonical import (
    Plant, Warehouse, Product, Material, BomLine, Supplier, SupplierMaterial,
    InventoryPolicy, InventorySnapshot, ProductionOrder, PurchaseOrder,
    DemandForecastLine, InventoryTransaction, Manager,
)
from repositories.inventory_repository import InventoryRepository
from repositories.bom_repository import BomRepository
from repositories.supplier_repository import SupplierRepository
from repositories.production_repository import ProductionRepository
from repositories.purchase_repository import PurchaseRepository


class Repository:
    """Master Repository facade combining all manufacturing sub-domain repositories."""

    def __init__(self, connector: BaseConnector | None = None):
        self.connector: BaseConnector = connector or get_connector()

        # Instantiate sub-domain repositories
        self._inventory_repo = InventoryRepository(self.connector)
        self._bom_repo = BomRepository(self.connector)
        self._supplier_repo = SupplierRepository(self.connector)
        self._production_repo = ProductionRepository(self.connector)
        self._purchase_repo = PurchaseRepository(self.connector)

        # Re-export entity lists for 100% backward compatibility
        self.plants: List[Plant] = self._inventory_repo.plants
        self.warehouses: List[Warehouse] = self._inventory_repo.warehouses
        self.products: List[Product] = self._bom_repo.products
        self.materials: List[Material] = self._bom_repo.materials
        self.bom: List[BomLine] = self._bom_repo.bom
        self.suppliers: List[Supplier] = self._supplier_repo.suppliers
        self.supplier_materials: List[SupplierMaterial] = self._supplier_repo.supplier_materials
        self.inventory_policies: List[InventoryPolicy] = self._inventory_repo.policies
        self.inventory: List[InventorySnapshot] = self._inventory_repo.inventory
        self.production_orders: List[ProductionOrder] = self._production_repo.production_orders
        self.purchase_orders: List[PurchaseOrder] = self._purchase_repo.purchase_orders
        self.demand_forecast: List[DemandForecastLine] = self._production_repo.demand_forecast
        self.inventory_transactions: List[InventoryTransaction] = self._purchase_repo.inventory_transactions
        self.managers: List[Manager] = self._purchase_repo.managers

        # Re-export index dictionaries
        self.material_by_id: Dict[str, Material] = self._bom_repo.material_by_id
        self.product_by_id: Dict[str, Product] = self._bom_repo.product_by_id
        self.plant_by_id: Dict[str, Plant] = self._inventory_repo.plant_by_id
        self.supplier_by_id: Dict[str, Supplier] = self._supplier_repo.supplier_by_id

        self.policy_by_key: Dict[Tuple[str, str], InventoryPolicy] = self._inventory_repo.policy_by_key
        self.inventory_by_key: Dict[Tuple[str, str], InventorySnapshot] = self._inventory_repo.inventory_by_key

        self.bom_by_product: Dict[str, List[BomLine]] = self._bom_repo.bom_by_product
        self.bom_by_material: Dict[str, List[BomLine]] = self._bom_repo.bom_by_material

        self.supplier_materials_by_material: Dict[str, List[SupplierMaterial]] = self._supplier_repo.supplier_materials_by_material
        self.open_pos_by_material_plant: Dict[Tuple[str, str], List[PurchaseOrder]] = self._purchase_repo.open_pos_by_material_plant
        self.production_orders_by_product_plant: Dict[Tuple[str, str], List[ProductionOrder]] = self._production_repo.production_orders_by_product_plant
        self.forecast_by_product_plant: Dict[Tuple[str, str], List[DemandForecastLine]] = self._production_repo.forecast_by_product_plant
        self.managers_by_plant: Dict[str, List[Manager]] = self._purchase_repo.managers_by_plant

    def products_using_material(self, material_id: str) -> List[BomLine]:
        return self._bom_repo.products_using_material(material_id)

    def _index(self) -> None:
        """Re-index data structures if internal lists are mutated directly by test patches."""
        self._inventory_repo.inventory_by_key = {
            (inv.material_id, inv.plant_id): inv for inv in self.inventory
        }
        self.inventory_by_key = self._inventory_repo.inventory_by_key
        self._inventory_repo.policy_by_key = {
            (p.material_id, p.plant_id): p for p in self.inventory_policies
        }
        self.policy_by_key = self._inventory_repo.policy_by_key


@lru_cache(maxsize=1)
def get_repository() -> Repository:
    """Singleton — the dataset is loaded once per process."""
    return Repository()


def clear_repository_cache():
    """Reset repository singleton cache."""
    get_repository.cache_clear()
