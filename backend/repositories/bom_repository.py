"""
BOM & Materials Domain Repository.
Reads materials, products, product families, and BOM component lines.
"""
from __future__ import annotations

from collections import defaultdict
from typing import List, Dict
from connectors.base import BaseConnector
from models.canonical import Material, Product, ProductFamily, BomLine


class BomRepository:
    def __init__(self, connector: BaseConnector):
        self.connector = connector
        self.materials: List[Material] = self.connector.get_materials()
        self.products: List[Product] = self.connector.get_products()
        self.product_families: List[ProductFamily] = self.connector.get_product_families()
        self.bom: List[BomLine] = self.connector.get_bom()

        self.material_by_id: Dict[str, Material] = {m.material_id: m for m in self.materials}
        self.product_by_id: Dict[str, Product] = {p.product_id: p for p in self.products}

        self.bom_by_product: Dict[str, List[BomLine]] = defaultdict(list)
        for line in self.bom:
            self.bom_by_product[line.product_id].append(line)

        self.bom_by_material: Dict[str, List[BomLine]] = defaultdict(list)
        for line in self.bom:
            self.bom_by_material[line.material_id].append(line)

    def products_using_material(self, material_id: str) -> List[BomLine]:
        return self.bom_by_material.get(material_id, [])

    def components_for_product(self, product_id: str) -> List[BomLine]:
        return self.bom_by_product.get(product_id, [])
