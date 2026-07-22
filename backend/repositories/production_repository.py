"""
Production Orders & Forecast Domain Repository.
"""
from __future__ import annotations

from collections import defaultdict
from typing import List, Dict, Tuple
from connectors.base import BaseConnector
from models.canonical import ProductionOrder, DemandForecastLine


class ProductionRepository:
    def __init__(self, connector: BaseConnector):
        self.connector = connector
        self.production_orders: List[ProductionOrder] = self.connector.get_production_orders()
        self.demand_forecast: List[DemandForecastLine] = self.connector.get_demand_forecast()

        self.production_orders_by_product_plant: Dict[Tuple[str, str], List[ProductionOrder]] = defaultdict(list)
        for po in self.production_orders:
            if po.status in ("Released", "In Process", "Confirmed", "Delayed"):
                self.production_orders_by_product_plant[(po.product_id, po.plant_id)].append(po)

        self.forecast_by_product_plant: Dict[Tuple[str, str], List[DemandForecastLine]] = defaultdict(list)
        for f in self.demand_forecast:
            self.forecast_by_product_plant[(f.product_id, f.plant_id)].append(f)
