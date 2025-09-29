# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""Pytest tests for CRUD operations."""

# -------------------------------------------

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.utils.database import Base
from app.crud.item import item_crud
from app.schemas.item import ItemCreate, ItemUpdate


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Import models to ensure they're registered
    from app.models.item import Item

    # Create tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_item_data():
    """Sample item data for testing."""
    return ItemCreate(
        name="Test Widget",
        description="A test widget for demo",
        price=29.99,  # Using float instead of Decimal for simplicity
    )


def test_create_item(db_session, sample_item_data):
    """Test creating a new item."""
    created_item = item_crud.create(db_session, sample_item_data)

    assert created_item.id is not None
    assert created_item.name == "Test Widget"
    assert created_item.description == "A test widget for demo"
    assert created_item.price == 29.99
    assert created_item.is_active is True


def test_get_item(db_session, sample_item_data):
    """Test retrieving an item by ID."""
    # Create item first
    created_item = item_crud.create(db_session, sample_item_data)

    # Retrieve item
    retrieved_item = item_crud.get(db_session, created_item.id)

    assert retrieved_item is not None
    assert retrieved_item.id == created_item.id
    assert retrieved_item.name == created_item.name


def test_get_nonexistent_item(db_session):
    """Test retrieving a non-existent item."""
    retrieved_item = item_crud.get(db_session, 999)
    assert retrieved_item is None


def test_update_item(db_session, sample_item_data):
    """Test updating an existing item."""
    # Create item first
    created_item = item_crud.create(db_session, sample_item_data)

    # Update item
    update_data = ItemUpdate(name="Updated Widget", price=39.99)
    updated_item = item_crud.update(db_session, created_item.id, update_data)

    assert updated_item is not None
    assert updated_item.name == "Updated Widget"
    assert updated_item.price == 39.99
    assert (
        updated_item.description == "A test widget for demo"
    )  # Should remain unchanged


def test_update_nonexistent_item(db_session):
    """Test updating a non-existent item."""
    update_data = ItemUpdate(name="Updated Widget")
    updated_item = item_crud.update(db_session, 999, update_data)
    assert updated_item is None


def test_get_multi_items(db_session):
    """Test retrieving multiple items."""
    # Create multiple items
    items_data = [ItemCreate(name=f"Item {i}", price=float(i * 10)) for i in range(5)]
    for item_data in items_data:
        item_crud.create(db_session, item_data)

    # Get items
    items = item_crud.get_multi(db_session, limit=10)

    assert len(items) == 5
    assert all(item.is_active for item in items)


def test_get_multi_with_filtering(db_session):
    """Test retrieving multiple items with filtering."""
    # Create items with different active states
    active_item = ItemCreate(name="Active Item", is_active=True)
    inactive_item = ItemCreate(name="Inactive Item", is_active=False)

    item_crud.create(db_session, active_item)
    created_inactive = item_crud.create(db_session, inactive_item)

    # Set one item to inactive manually
    created_inactive.is_active = False
    db_session.commit()

    # Get only active items
    active_items = item_crud.get_multi(db_session, is_active=True)
    inactive_items = item_crud.get_multi(db_session, is_active=False)

    assert len(active_items) == 1
    assert len(inactive_items) == 1


def test_soft_delete_item(db_session, sample_item_data):
    """Test soft deleting an item."""
    # Create item first
    created_item = item_crud.create(db_session, sample_item_data)

    # Soft delete
    deleted_item = item_crud.delete(db_session, created_item.id)

    assert deleted_item is not None
    assert deleted_item.is_active is False


def test_hard_delete_item(db_session, sample_item_data):
    """Test permanently deleting an item."""
    # Create item first
    created_item = item_crud.create(db_session, sample_item_data)

    # Hard delete
    result = item_crud.hard_delete(db_session, created_item.id)

    assert result is True

    # Verify item is gone
    retrieved_item = item_crud.get(db_session, created_item.id)
    assert retrieved_item is None


def test_count_items(db_session):
    """Test counting items."""
    # Create items
    items_data = [
        ItemCreate(name=f"Item {i}", is_active=(i % 2 == 0)) for i in range(4)
    ]
    for item_data in items_data:
        item_crud.create(db_session, item_data)

    # Count all items
    total_count = item_crud.count(db_session)
    active_count = item_crud.count(db_session, is_active=True)
    inactive_count = item_crud.count(db_session, is_active=False)

    assert total_count == 4
    assert active_count == 2
    assert inactive_count == 2


def test_search_by_name(db_session):
    """Test searching items by name."""
    # Create items with different names
    items_data = [
        ItemCreate(name="Red Widget"),
        ItemCreate(name="Blue Widget"),
        ItemCreate(name="Green Gadget"),
    ]
    for item_data in items_data:
        item_crud.create(db_session, item_data)

    # Search for widgets
    widget_results = item_crud.search_by_name(db_session, "widget")
    gadget_results = item_crud.search_by_name(db_session, "gadget")

    assert len(widget_results) == 2
    assert len(gadget_results) == 1
    assert all("widget" in item.name.lower() for item in widget_results)
