"""
Unit and integration tests for Pluggable Enterprise Data Connectors & Factory.
"""
import pytest
from connectors.connector_factory import ConnectorFactory
from connectors.registry import list_registered_connectors, get_connector_class
from connectors.csv_connector import CsvConnector
from connectors.excel_connector import ExcelConnector
from connectors.sqlserver_connector import SqlServerConnector
from connectors.fabric_connector import FabricConnector
from connectors.sap_connector import SapConnector


def test_registered_connectors_list():
    connectors = list_registered_connectors()
    expected = ["csv", "excel", "sqlserver", "postgres", "fabric", "sap", "rest", "blob", "sharepoint"]
    for conn in expected:
        assert conn in connectors


def test_connector_factory_creation():
    csv_conn = ConnectorFactory.create(data_source="csv", force_new=True)
    assert isinstance(csv_conn, CsvConnector)

    sql_conn = ConnectorFactory.create(data_source="sqlserver", force_new=True)
    assert isinstance(sql_conn, SqlServerConnector)

    fabric_conn = ConnectorFactory.create(data_source="fabric", force_new=True)
    assert isinstance(fabric_conn, FabricConnector)

    sap_conn = ConnectorFactory.create(data_source="sap", force_new=True)
    assert isinstance(sap_conn, SapConnector)


def test_csv_connector_loads_canonical_models():
    conn = ConnectorFactory.create(data_source="csv", force_new=True)
    materials = conn.load_materials()
    assert len(materials) > 0
    assert hasattr(materials[0], "material_id")

    inventory = conn.load_inventory()
    assert len(inventory) > 0
    assert hasattr(inventory[0], "usable_qty")

    bom = conn.load_bom()
    assert len(bom) > 0
    assert hasattr(bom[0], "quantity_per_unit")
