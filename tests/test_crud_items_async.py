# -------------------------------------------
# Author: Nils Gies
# -------------------------------------------
"""Async pytest tests for Item CRUD operations."""
# -------------------------------------------

import pytest
import pytest_asyncio
from dataclasses import asdict
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.utils.database import Base
from app.crud.item import item_crud
from app.dataclasses.item import ItemData, ItemUpdateData


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh in-memory async DB session per test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # Import models to ensure they're registered
    from app.models.item import Item  # noqa

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingSessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )

    async with TestingSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def sample_item_data():
    return ItemData(
        name="Test Widget",
        description="A test widget for demo",
        price=29.99,
        is_active=True,
    )


@pytest.mark.anyio
async def test_create_item(db_session, sample_item_data):
    """Test creating a new item."""
    created_item = await item_crud.create(db_session, asdict(sample_item_data))
    assert created_item.id is not None
    assert created_item.name == sample_item_data.name
    assert created_item.description == sample_item_data.description
    assert created_item.price == sample_item_data.price
    assert created_item.is_active is True


@pytest.mark.anyio
async def test_get_item(db_session, sample_item_data):
    """Test retrieving an item by ID."""
    created = await item_crud.create(db_session, asdict(sample_item_data))
    fetched = await item_crud.get(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == created.name


@pytest.mark.anyio
async def test_get_nonexistent_item(db_session):
    """Test retrieving a non-existent item."""
    assert await item_crud.get(db_session, 999) is None


@pytest.mark.anyio
async def test_update_item(db_session, sample_item_data):
    """Test updating an existing item."""
    created = await item_crud.create(db_session, asdict(sample_item_data))
    update = ItemUpdateData(name="Updated Widget", price=39.99)
    updated = await item_crud.update(db_session, created.id, update.to_patch_dict())
    assert updated is not None
    assert updated.name == "Updated Widget"
    assert updated.price == 39.99
    assert updated.description == sample_item_data.description


@pytest.mark.anyio
async def test_update_nonexistent_item(db_session):
    """Test updating a non-existent item."""
    update = ItemUpdateData(name="Does Not Exist")
    assert await item_crud.update(db_session, 999, update.to_patch_dict()) is None


@pytest.mark.anyio
async def test_get_multi_items(db_session):
    """Test retrieving multiple items."""
    for i in range(5):
        data = ItemData(
            name=f"Item {i}", description=None, price=float(i * 10), is_active=True
        )
        await item_crud.create(db_session, asdict(data))
    items = await item_crud.get_multi(db_session, limit=10)
    assert len(items) == 5
    assert all(it.is_active for it in items)


@pytest.mark.anyio
async def test_get_multi_with_filtering(db_session):
    """Test retrieving multiple items with filtering."""
    active = ItemData(name="Active Item", description=None, price=1.0, is_active=True)
    inactive = ItemData(
        name="Inactive Item", description=None, price=2.0, is_active=False
    )
    await item_crud.create(db_session, asdict(active))
    await item_crud.create(db_session, asdict(inactive))
    active_list = await item_crud.get_multi(db_session, is_active=True)
    inactive_list = await item_crud.get_multi(db_session, is_active=False)
    assert len(active_list) == 1
    assert len(inactive_list) == 1


@pytest.mark.anyio
async def test_soft_delete_item(db_session, sample_item_data):
    """Test soft deleting an item."""
    created = await item_crud.create(db_session, asdict(sample_item_data))
    deleted = await item_crud.delete(db_session, created.id)
    assert deleted is not None
    assert deleted.is_active is False


@pytest.mark.anyio
async def test_hard_delete_item(db_session, sample_item_data):
    """Test permanently deleting an item."""
    created = await item_crud.create(db_session, asdict(sample_item_data))
    ok = await item_crud.hard_delete(db_session, created.id)
    assert ok is True
    assert await item_crud.get(db_session, created.id) is None


@pytest.mark.anyio
async def test_count_items(db_session):
    """Test counting items."""
    for i in range(4):
        data = ItemData(
            name=f"Item {i}",
            description=None,
            price=0.0,
            is_active=(i % 2 == 0),
        )
        await item_crud.create(db_session, asdict(data))
    assert await item_crud.count(db_session) == 4
    assert await item_crud.count(db_session, is_active=True) == 2
    assert await item_crud.count(db_session, is_active=False) == 2


@pytest.mark.anyio
async def test_search_by_name(db_session):
    """Test searching items by name."""
    names = ["Red Widget", "Blue Widget", "Green Gadget"]
    for n in names:
        await item_crud.create(
            db_session,
            asdict(ItemData(name=n, description=None, price=1.0, is_active=True)),
        )
    widgets = await item_crud.search_by_name(db_session, "widget")
    gadgets = await item_crud.search_by_name(db_session, "gadget")
    assert len(widgets) == 2
    assert len(gadgets) == 1
    assert all("widget" in w.name.lower() for w in widgets)
