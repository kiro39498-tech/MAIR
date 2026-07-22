"""
Unit tests for Domain Repositories & Master Repository Facade.
"""
import pytest
from data.repository import get_repository, clear_repository_cache, Repository
from connectors.connector_factory import ConnectorFactory


def test_master_repository_facade():
    clear_repository_cache()
    repo = get_repository()

    assert len(repo.materials) > 0
    assert len(repo.inventory) > 0
    assert len(repo.bom) > 0
    assert len(repo.suppliers) > 0

    # Verify indexing structures
    assert len(repo.material_by_id) > 0
    assert len(repo.policy_by_key) > 0
    assert len(repo.inventory_by_key) > 0


def test_products_using_material_lookup():
    repo = get_repository()
    sample_material_id = repo.materials[0].material_id
    boms = repo.products_using_material(sample_material_id)
    assert isinstance(boms, list)
