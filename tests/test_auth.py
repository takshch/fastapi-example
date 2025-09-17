"""
Tests for authentication endpoints.

This module contains tests for all authentication-related API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test class for authentication endpoints."""
    
    async def test_register_user_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "password": "newpassword123"
        }
        
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert "id" in data
    
    async def test_register_user_duplicate(self, client: AsyncClient):
        """Test user registration with duplicate username."""
        user_data = {
            "username": "duplicateuser",
            "password": "password123"
        }
        
        # Register first time
        response1 = await client.post("/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Try to register again with same username
        response2 = await client.post("/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]
    
    async def test_register_user_invalid_data(self, client: AsyncClient):
        """Test user registration with invalid data."""
        invalid_data = {
            "username": "ab",  # Too short
            "password": "123"  # Too short
        }
        
        response = await client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    async def test_login_success(self, client: AsyncClient):
        """Test successful user login."""
        user_data = {
            "username": "logintest",
            "password": "logintest123"
        }
        
        # Register user first
        await client.post("/auth/register", json=user_data)
        
        # Login
        response = await client.post("/auth/login", data=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        user_data = {
            "username": "invaliduser",
            "password": "wrongpassword"
        }
        
        response = await client.post("/auth/login", data=user_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        user_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        response = await client.post("/auth/login", data=user_data)
        assert response.status_code == 401
    
    async def test_protected_endpoint_with_valid_token(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test accessing protected endpoint with valid token."""
        employee_data = {
            "name": "Test Employee",
            "department": "Engineering",
            "salary": 70000.0,
            "joining_date": "2023-01-01",
            "skills": ["Python"]
        }
        
        response = await client.post(
            "/employees",
            json=employee_data,
            headers=auth_headers
        )
        assert response.status_code == 201
    
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token."""
        employee_data = {
            "name": "Test Employee",
            "department": "Engineering",
            "salary": 70000.0,
            "joining_date": "2023-01-01",
            "skills": ["Python"]
        }
        
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = await client.post(
            "/employees",
            json=employee_data,
            headers=invalid_headers
        )
        assert response.status_code == 401
    
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        employee_data = {
            "name": "Test Employee",
            "department": "Engineering",
            "salary": 70000.0,
            "joining_date": "2023-01-01",
            "skills": ["Python"]
        }
        
        response = await client.post("/employees", json=employee_data)
        assert response.status_code == 401
