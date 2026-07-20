from datetime import timezone
import os
import csv
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from config.settings import settings

class BaseExecutionConnector(ABC):
    @abstractmethod
    def create_purchase_order(self, material_id: str, plant_id: str, supplier_id: str, qty: int) -> str:
        pass


class MockExecutionConnector(BaseExecutionConnector):
    def _get_supplier_info(self, material_id: str, supplier_id: str):
        sm_file = os.path.join(settings.csv_data_dir, "supplier_materials.csv")
        try:
            with open(sm_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['material_id'] == material_id and row['supplier_id'] == supplier_id:
                        return float(row['unit_price']), int(row['lead_time_days'])
        except FileNotFoundError:
            pass
        return 0.0, 14  # Defaults if not found

    def create_purchase_order(self, material_id: str, plant_id: str, supplier_id: str, qty: int) -> str:
        created_file = os.path.join(settings.csv_data_dir, "purchase_orders_created.csv")
        
        file_exists = os.path.exists(created_file)
        po_count = 1
        
        if file_exists:
            with open(created_file, mode='r', encoding='utf-8') as f:
                po_count = sum(1 for _ in f)  # Header is row 1, data starts at 2
                
        po_id = f"PO-EXEC-{po_count}"
        
        unit_price, lead_time_days = self._get_supplier_info(material_id, supplier_id)
        order_date = datetime.now(timezone.utc).date()
        expected_receipt_date = order_date + timedelta(days=lead_time_days)
        
        with open(created_file, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "po_id", "po_line", "material_id", "supplier_id", "plant_id",
                    "order_qty", "open_qty", "unit_price", "order_date", 
                    "expected_receipt_date", "status"
                ])
            
            writer.writerow([
                po_id, 1, material_id, supplier_id, plant_id,
                qty, qty, unit_price, order_date.isoformat(),
                expected_receipt_date.isoformat(), "Open"
            ])
            
        return po_id

def get_execution_connector() -> BaseExecutionConnector:
    return MockExecutionConnector()
