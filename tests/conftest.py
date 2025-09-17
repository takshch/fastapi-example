"""
Pytest configuration and fixtures.

This module provides common fixtures and configuration for all tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from main import app
from app.database import db_manager
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create a test database connection."""
    # Use a test database
    test_db_name = f"{settings.database_name}_test"
    
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[test_db_name]
    
    yield database
    
    # Cleanup: drop the test database
    await client.drop_database(test_db_name)
    client.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sync_client() -> TestClient:
    """Create a synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Create authentication headers for testing."""
    # Register a test user
    user_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    await client.post("/auth/register", json=user_data)
    
    # Login to get token
    response = await client.post("/auth/login", data=user_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def sample_employee_data() -> dict:
    """Sample employee data for testing."""
    return {
        "name": "John Doe",
        "department": "Engineering",
        "salary": 75000.0,
        "joining_date": "2023-01-15",
        "skills": ["Python", "MongoDB", "APIs"]
    }


@pytest.fixture
async def sample_employees_data() -> list[dict]:
    """Sample multiple employees data for testing."""
    return [
        {
            "name": "John Doe",
            "department": "Engineering",
            "salary": 75000.0,
            "joining_date": "2023-01-15",
            "skills": ["Python", "MongoDB", "APIs"]
        },
        {
            "name": "Jane Smith",
            "department": "Engineering",
            "salary": 85000.0,
            "joining_date": "2023-02-20",
            "skills": ["JavaScript", "React", "Node.js"]
        },
        {
            "name": "Mike Johnson",
            "department": "HR",
            "salary": 60000.0,
            "joining_date": "2023-03-10",
            "skills": ["Recruitment", "Employee Relations", "HRIS"]
        }
    ]
