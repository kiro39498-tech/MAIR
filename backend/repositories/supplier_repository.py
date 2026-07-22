"""
Supplier Domain Repository.
"""
from __future__ import annotations

from collections import defaultdict
from typing import List, Dict
from connectors.base import BaseConnector
from models.canonical import Supplier, SupplierMaterial


class SupplierRepository:
    def __init__(self, connector: BaseConnector):
        self.connector = connector
        self.suppliers: List[Supplier] = self.connector.get_suppliers()
        self.supplier_materials: List[SupplierMaterial] = self.connector.get_supplier_materials()

        self.supplier_by_id: Dict[str, Supplier] = {s.supplier_id: s for s in self.suppliers}
        self.supplier_materials_by_material: Dict[str, List[SupplierMaterial]] = defaultdict(list)
        for sm in self.supplier_materials:
            self.supplier_materials_by_material[sm.material_id].append(sm)

    def suppliers_for_material(self, material_id: str) -> List[SupplierMaterial]:
        return self.supplier_materials_by_material.get(material_id, [])
