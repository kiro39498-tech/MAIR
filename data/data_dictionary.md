# Material Availability & Inventory Replenishment Agent — Dataset Data Dictionary

This dataset contains synthesized ERP-style inventory, procurement, production, and planning data for a multi-plant manufacturing scenario.

## plants.csv
| Field | Description |
|---|---|
| plant_id | Primary key. Unique plant identifier. |
| plant_name | Human-readable plant name. |
| country | Country where the plant is located. |
| region | Geographic region for the plant. |
| plant_type | Plant classification (e.g. make-to-stock, make-to-order, distribution). |
| timezone | Plant local timezone used for scheduling and planning. |

## warehouses.csv
| Field | Description |
|---|---|
| warehouse_id | Primary key. Unique warehouse identifier. |
| plant_id | Foreign key to `plants.plant_id`. |
| warehouse_type | Warehouse role, typically `RM`, `WIP`, or `FG`. |
| capacity_units | Storage capacity in abstract units. |

## product_families.csv
| Field | Description |
|---|---|
| family_id | Primary key. Product family identifier. |
| family_name | Product family descriptive name. |

## products.csv
| Field | Description |
|---|---|
| product_id | Primary key. Unique product identifier. |
| family_id | Foreign key to `product_families.family_id`. |
| product_name | Product description/name. |
| primary_plant_id | Foreign key to `plants.plant_id`. |
| standard_cost | Standard cost of the product. |
| lifecycle_status | Product lifecycle phase (e.g. Active, Phase Out, Obsolete). |

## materials.csv
| Field | Description |
|---|---|
| material_id | Primary key. Unique material identifier. |
| material_name | Material description. |
| material_type | Material classification (Raw Material / Component / Packaging / Electronic / Fastener). |
| criticality | Business-criticality rating (High / Medium / Low). |
| abc_class | ABC inventory classification (A / B / C). |
| uom | Unit of measure. |

## bom.csv
| Field | Description |
|---|---|
| product_id | Foreign key to `products.product_id`. |
| material_id | Foreign key to `materials.material_id`. |
| quantity_per_unit | Quantity of material required per unit of product. |

## suppliers.csv
| Field | Description |
|---|---|
| supplier_id | Primary key. Unique supplier identifier. |
| supplier_name | Supplier name. |
| country | Supplier country. |
| reliability_score | Synthetic supplier reliability or on-time performance score. |

## supplier_materials.csv
| Field | Description |
|---|---|
| supplier_id | Foreign key to `suppliers.supplier_id`. |
| material_id | Foreign key to `materials.material_id`. |
| unit_price | Supplier unit cost for the material. |
| lead_time_days | Supplier lead time in days. |
| moq | Minimum order quantity required by the supplier. |
| is_primary_supplier | Indicates whether this supplier is the primary source for the material. |

## inventory_policies.csv
| Field | Description |
|---|---|
| material_id | Foreign key to `materials.material_id`. |
| plant_id | Foreign key to `plants.plant_id`. |
| avg_daily_usage | Average daily consumption rate for the material at the plant. |
| safety_stock_qty | Safety stock quantity for the material at the plant. |
| reorder_point_qty | Reorder point quantity for the material at the plant. |
| max_stock_qty | Maximum allowed stock quantity. |
| reorder_qty | Default reorder quantity. |

## inventory.csv
| Field | Description |
|---|---|
| material_id | Foreign key to `materials.material_id`. |
| plant_id | Foreign key to `plants.plant_id`. |
| unrestricted_qty | Usable stock currently available. |
| quality_hold_qty | Stock held for quality inspection or quarantine. |
| blocked_qty | Stock blocked from use. |
| reserved_qty | Stock reserved for open production orders or commitments. |
| last_count_date | Last inventory count date. |

## production_orders.csv
| Field | Description |
|---|---|
| production_order_id | Primary key. Unique production order identifier. |
| product_id | Foreign key to `products.product_id`. |
| plant_id | Foreign key to `plants.plant_id`. |
| order_qty | Quantity ordered/produced. |
| start_date | Planned production start date. |
| finish_date | Planned production completion date. |
| status | Production order status (Released, In Process, Confirmed, Delayed). |
| priority | Production priority level. |

## purchase_orders.csv
| Field | Description |
|---|---|
| purchase_order_id | Primary key. Unique purchase order identifier. |
| supplier_id | Foreign key to `suppliers.supplier_id`. |
| material_id | Foreign key to `materials.material_id`. |
| plant_id | Foreign key to `plants.plant_id`. |
| order_qty | Quantity ordered. |
| order_date | Purchase order creation date. |
| expected_receipt_date | Expected material receipt date. |
| status | Purchase order status, including open and late conditions. |

## demand_forecast.csv
| Field | Description |
|---|---|
| forecast_id | Primary key or identifier for the forecast row. |
| product_id | Foreign key to `products.product_id`. |
| plant_id | Foreign key to `plants.plant_id`. |
| forecast_week | Forecast week identifier. |
| forecast_qty | Forecasted demand quantity for that week. |

## inventory_transactions.csv
| Field | Description |
|---|---|
| transaction_id | Primary key. Unique transaction identifier. |
| material_id | Foreign key to `materials.material_id`. |
| plant_id | Foreign key to `plants.plant_id`. |
| warehouse_id | Foreign key to `warehouses.warehouse_id`. |
| transaction_type | Transaction type (Goods Receipt, Goods Issue, Transfer, Adjustment). |
| quantity | Transaction quantity. |
| transaction_date | Transaction date. |
| related_order_id | Associated production or purchase order identifier. |

## managers.csv
| Field | Description |
|---|---|
| manager_id | Primary key. Unique manager identifier. |
| manager_name | Manager name. |
| role | Manager role (Plant Manager, Inventory Manager, Procurement Manager). |
| plant_id | Foreign key to `plants.plant_id`. |
| contact_channel | Notification channel (Email, Teams, etc.). |
| approval_threshold_value | Threshold value used for approval or escalation. |

## _answer_key_inventory_status.csv
This file contains the ground truth inventory health status used for validation. It should not be used as an input to the analytics engine.

| Field | Description |
|---|---|
| material_id | Foreign key to `materials.material_id`. |
| plant_id | Foreign key to `plants.plant_id`. |
| usable_inventory | Expected usable inventory value. |
| inventory_status | Ground truth status label. |

---

## Notes
- `VITE_API_BASE_URL` in frontend config points at `http://127.0.0.1:8002`.
- Backend API port is configured as `8002`.
- `PORT=8001` in frontend `.env` is the Vite dev server port, not the backend port.
- The dataset includes linked planning, production, procurement, inventory, and transaction records for a realistic materials availability scenario.
