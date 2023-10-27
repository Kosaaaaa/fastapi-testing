from __future__ import annotations

from collections.abc import Generator

import fastapi
from fastapi.testclient import TestClient
from main import Base, app, get_db
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker


# Setup the TestClient
client = TestClient(app)

# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db() -> Generator[Session, None, None]:
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


def test_create_item() -> None:
    response = client.post("/items/", json={"name": "Test Item", "description": "This is a test item"})
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "This is a test item"
    assert "id" in data


def test_read_item() -> None:
    # Create an item
    response = client.post("/items/", json={"name": "Test Item", "description": "This is a test item"})
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    data = response.json()
    item_id = data["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "This is a test item"
    assert data["id"] == item_id


def test_update_item() -> None:
    item_id = 1
    response = client.put(
        f"/items/{item_id}",
        json={"name": "Updated Item", "description": "This is an updated item"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    data = response.json()
    assert data["name"] == "Updated Item"
    assert data["description"] == "This is an updated item"
    assert data["id"] == item_id


def test_delete_item() -> None:
    item_id = 1
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == fastapi.status.HTTP_200_OK, response.text
    data = response.json()
    assert data["id"] == item_id
    # Try to get the deleted item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND, response.text


def setup() -> None:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)


def teardown() -> None:
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)
