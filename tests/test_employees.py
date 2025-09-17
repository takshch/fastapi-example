"""
Tests for employee endpoints.

This module contains tests for all employee-related API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestEmployeeEndpoints:
    """Test class for employee endpoints."""
    
    async def test_create_employee_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employee_data: dict
    ):
        """Test successful employee creation."""
        response = await client.post(
            "/employees",
            json=sample_employee_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_employee_data["name"]
        assert data["department"] == sample_employee_data["department"]
        assert data["salary"] == sample_employee_data["salary"]
        assert data["joining_date"] == sample_employee_data["joining_date"]
        assert data["skills"] == sample_employee_data["skills"]
        assert "id" in data
        assert data["id"].startswith("E")
    
    async def test_create_employee_unauthorized(
        self, 
        client: AsyncClient, 
        sample_employee_data: dict
    ):
        """Test employee creation without authentication."""
        response = await client.post("/employees", json=sample_employee_data)
        assert response.status_code == 401
    
    async def test_create_employee_invalid_data(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test employee creation with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "department": "Engineering",
            "salary": -1000,  # Negative salary
            "joining_date": "invalid-date",
            "skills": []  # Empty skills
        }
        
        response = await client.post(
            "/employees",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422
    
    async def test_get_employee_by_id_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employee_data: dict
    ):
        """Test successful employee retrieval by ID."""
        # Create employee first
        create_response = await client.post(
            "/employees",
            json=sample_employee_data,
            headers=auth_headers
        )
        employee_id = create_response.json()["id"]
        
        # Get employee
        response = await client.get(f"/employees/{employee_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == employee_id
        assert data["name"] == sample_employee_data["name"]
    
    async def test_get_employee_by_id_not_found(self, client: AsyncClient):
        """Test employee retrieval with non-existent ID."""
        response = await client.get("/employees/E999")
        assert response.status_code == 404
    
    async def test_list_employees_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employees_data: list
    ):
        """Test successful employee listing."""
        # Create multiple employees
        for employee_data in sample_employees_data:
            await client.post(
                "/employees",
                json=employee_data,
                headers=auth_headers
            )
        
        # List employees
        response = await client.get("/employees")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= len(sample_employees_data)
    
    async def test_list_employees_with_pagination(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employees_data: list
    ):
        """Test employee listing with pagination."""
        # Create multiple employees
        for employee_data in sample_employees_data:
            await client.post(
                "/employees",
                json=employee_data,
                headers=auth_headers
            )
        
        # List employees with pagination
        response = await client.get("/employees?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "meta" in data
        assert len(data["items"]) <= 2
        assert data["meta"]["page"] == 1
        assert data["meta"]["page_size"] == 2
    
    async def test_list_employees_by_department(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employees_data: list
    ):
        """Test employee listing filtered by department."""
        # Create multiple employees
        for employee_data in sample_employees_data:
            await client.post(
                "/employees",
                json=employee_data,
                headers=auth_headers
            )
        
        # List Engineering employees
        response = await client.get("/employees?department=Engineering")
        assert response.status_code == 200
        data = response.json()
        for employee in data:
            assert employee["department"] == "Engineering"
    
    async def test_search_employees_by_skill(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employees_data: list
    ):
        """Test employee search by skill."""
        # Create multiple employees
        for employee_data in sample_employees_data:
            await client.post(
                "/employees",
                json=employee_data,
                headers=auth_headers
            )
        
        # Search for Python developers
        response = await client.get("/employees/search?skill=Python")
        assert response.status_code == 200
        data = response.json()
        for employee in data:
            assert "Python" in employee["skills"]
    
    async def test_search_employees_with_pagination(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employees_data: list
    ):
        """Test employee search with pagination."""
        # Create multiple employees
        for employee_data in sample_employees_data:
            await client.post(
                "/employees",
                json=employee_data,
                headers=auth_headers
            )
        
        # Search with pagination
        response = await client.get("/employees/search?skill=Python&page=1&page_size=1")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "meta" in data
        assert len(data["items"]) <= 1
    
    async def test_update_employee_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employee_data: dict
    ):
        """Test successful employee update."""
        # Create employee first
        create_response = await client.post(
            "/employees",
            json=sample_employee_data,
            headers=auth_headers
        )
        employee_id = create_response.json()["id"]
        
        # Update employee
        update_data = {"salary": 80000.0, "skills": ["Python", "FastAPI", "Docker"]}
        response = await client.put(
            f"/employees/{employee_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["salary"] == 80000.0
        assert data["skills"] == ["Python", "FastAPI", "Docker"]
    
    async def test_update_employee_unauthorized(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employee_data: dict
    ):
        """Test employee update without authentication."""
        # Create employee first
        create_response = await client.post(
            "/employees",
            json=sample_employee_data,
            headers=auth_headers
        )
        employee_id = create_response.json()["id"]
        
        # Try to update without auth
        update_data = {"salary": 80000.0}
        response = await client.put(f"/employees/{employee_id}", json=update_data)
        assert response.status_code == 401
    
    async def test_delete_employee_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employee_data: dict
    ):
        """Test successful employee deletion."""
        # Create employee first
        create_response = await client.post(
            "/employees",
            json=sample_employee_data,
            headers=auth_headers
        )
        employee_id = create_response.json()["id"]
        
        # Delete employee
        response = await client.delete(f"/employees/{employee_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify employee is deleted
        get_response = await client.get(f"/employees/{employee_id}")
        assert get_response.status_code == 404
    
    async def test_delete_employee_unauthorized(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employee_data: dict
    ):
        """Test employee deletion without authentication."""
        # Create employee first
        create_response = await client.post(
            "/employees",
            json=sample_employee_data,
            headers=auth_headers
        )
        employee_id = create_response.json()["id"]
        
        # Try to delete without auth
        response = await client.delete(f"/employees/{employee_id}")
        assert response.status_code == 401
    
    async def test_get_average_salary_by_department(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        sample_employees_data: list
    ):
        """Test average salary aggregation by department."""
        # Create multiple employees
        for employee_data in sample_employees_data:
            await client.post(
                "/employees",
                json=employee_data,
                headers=auth_headers
            )
        
        # Get average salary by department
        response = await client.get("/employees/avg-salary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that we have data for different departments
        departments = [item["department"] for item in data]
        assert "Engineering" in departments
        assert "HR" in departments
