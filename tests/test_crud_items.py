# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""Pytest tests for Item CRUD operations (decoupled from Pydantic)."""
# -------------------------------------------

import pytest
from dataclasses import asdict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.utils.database import Base
from app.crud.item import item_crud
from app.dataclasses.item import ItemData, ItemUpdateData


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory DB session per test."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_item_data():
    return ItemData(
        name="Test Widget",
        description="A test widget for demo",
        price=29.99,
        is_active=True,
    )


def test_create_item(db_session, sample_item_data):
    created_item = item_crud.create(db_session, asdict(sample_item_data))
    assert created_item.id is not None
    assert created_item.name == sample_item_data.name
    assert created_item.description == sample_item_data.description
    assert created_item.price == sample_item_data.price
    assert created_item.is_active is True


def test_get_item(db_session, sample_item_data):
    created = item_crud.create(db_session, asdict(sample_item_data))
    fetched = item_crud.get(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == created.name


def test_get_nonexistent_item(db_session):
    assert item_crud.get(db_session, 999) is None


def test_update_item(db_session, sample_item_data):
    created = item_crud.create(db_session, asdict(sample_item_data))
    update = ItemUpdateData(name="Updated Widget", price=39.99)
    updated = item_crud.update(db_session, created.id, update.to_patch_dict())
    assert updated is not None
    assert updated.name == "Updated Widget"
    assert updated.price == 39.99
    assert updated.description == sample_item_data.description


def test_update_nonexistent_item(db_session):
    update = ItemUpdateData(name="Does Not Exist")
    assert item_crud.update(db_session, 999, update.to_patch_dict()) is None


def test_get_multi_items(db_session):
    for i in range(5):
        data = ItemData(
            name=f"Item {i}", description=None, price=float(i * 10), is_active=True
        )
        item_crud.create(db_session, asdict(data))
    items = item_crud.get_multi(db_session, limit=10)
    assert len(items) == 5
    assert all(it.is_active for it in items)


def test_get_multi_with_filtering(db_session):
    active = ItemData(name="Active Item", description=None, price=1.0, is_active=True)
    inactive = ItemData(
        name="Inactive Item", description=None, price=2.0, is_active=False
    )
    item_crud.create(db_session, asdict(active))
    item_crud.create(db_session, asdict(inactive))
    active_list = item_crud.get_multi(db_session, is_active=True)
    inactive_list = item_crud.get_multi(db_session, is_active=False)
    assert len(active_list) == 1
    assert len(inactive_list) == 1


def test_soft_delete_item(db_session, sample_item_data):
    created = item_crud.create(db_session, asdict(sample_item_data))
    deleted = item_crud.delete(db_session, created.id)
    assert deleted is not None
    assert deleted.is_active is False


def test_hard_delete_item(db_session, sample_item_data):
    created = item_crud.create(db_session, asdict(sample_item_data))
    ok = item_crud.hard_delete(db_session, created.id)
    assert ok is True
    assert item_crud.get(db_session, created.id) is None


def test_count_items(db_session):
    for i in range(4):
        data = ItemData(
            name=f"Item {i}",
            description=None,
            price=0.0,
            is_active=(i % 2 == 0),
        )
        item_crud.create(db_session, asdict(data))
    assert item_crud.count(db_session) == 4
    assert item_crud.count(db_session, is_active=True) == 2
    assert item_crud.count(db_session, is_active=False) == 2


def test_search_by_name(db_session):
    names = ["Red Widget", "Blue Widget", "Green Gadget"]
    for n in names:
        item_crud.create(
            db_session,
            asdict(ItemData(name=n, description=None, price=1.0, is_active=True)),
        )
    widgets = item_crud.search_by_name(db_session, "widget")
    gadgets = item_crud.search_by_name(db_session, "gadget")
    assert len(widgets) == 2
    assert len(gadgets) == 1
    assert all("widget" in w.name.lower() for w in widgets)
