"""
Employee service for managing employee data.

This module provides business logic for employee operations including
CRUD operations, search, and pagination.
"""

from typing import List, Optional, Dict, Any, Tuple
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
import math

from app.services.base import BaseService
from app.schemas.employee import Employee, EmployeeCreate, EmployeeUpdate
from app.schemas.pagination import PaginationMeta
from app.core.exceptions import EmployeeNotFoundError, EmployeeAlreadyExistsError, ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmployeeService(BaseService[Employee]):
    """Service for managing employee data."""
    
    def __init__(self):
        super().__init__("employees")

    async def generate_next_employee_id(self) -> str:
        """Generate the next employee ID in sequence (E001, E002, etc.)"""
        collection = await self.get_collection()
        
        # Find the highest existing employee_id
        pipeline = [
            {
                "$match": {
                    "employee_id": {"$regex": "^E[0-9]+$"}
                }
            },
            {
                "$addFields": {
                    "numeric_id": {
                        "$toInt": {"$substr": ["$employee_id", 1, -1]}
                    }
                }
            },
            {
                "$sort": {"numeric_id": -1}
            },
            {
                "$limit": 1
            }
        ]
        
        result = await collection.aggregate(pipeline).to_list(1)
        
        if result:
            # Get the highest numeric ID and increment it
            highest_numeric = result[0]["numeric_id"]
            next_numeric = highest_numeric + 1
        else:
            # No existing employees, start with E001
            next_numeric = 1
        
        # Format as E001, E002, etc.
        return f"E{next_numeric:03d}"

    async def validate_document(self, document: Dict[str, Any]) -> None:
        """
        Validate employee document data.
        
        Args:
            document: Employee document data
            
        Raises:
            ValidationError: If validation fails
        """
        required_fields = ["name", "department", "salary", "joining_date", "skills"]
        
        for field in required_fields:
            if field not in document:
                raise ValidationError(f"Missing required field: {field}")
        
        if not isinstance(document["skills"], list) or len(document["skills"]) == 0:
            raise ValidationError("Skills must be a non-empty list")
        
        if document["salary"] <= 0:
            raise ValidationError("Salary must be positive")
    
    async def create_employee(self, employee: EmployeeCreate) -> Employee:
        """
        Create a new employee with auto-generated employee_id.
        
        Args:
            employee: Employee creation data
            
        Returns:
            Employee: Created employee object
            
        Raises:
            EmployeeAlreadyExistsError: If employee already exists
            ValidationError: If validation fails
        """
        # Generate the next employee ID
        employee_id = await self.generate_next_employee_id()
        
        # Create employee data with generated ID
        employee_dict = employee.dict()
        employee_dict["employee_id"] = employee_id
        
        # Validate document
        await self.validate_document(employee_dict)
        
        try:
            # Create document
            document_id = await self.create_document(employee_dict)
            
            # Fetch the created employee
            created_employee = await self.get_document_by_id(document_id)
            if not created_employee:
                raise EmployeeNotFoundError(employee_id)
            
            logger.info(f"Created employee: {employee_id}")
            return Employee(**created_employee)
            
        except DuplicateKeyError:
            raise EmployeeAlreadyExistsError(employee_id)

    async def get_employee_by_id(self, employee_id: str) -> Employee:
        """
        Get employee by employee_id.
        
        Args:
            employee_id: Employee ID to search for
            
        Returns:
            Employee: Employee object
            
        Raises:
            EmployeeNotFoundError: If employee not found
        """
        collection = await self.get_collection()
        employee = await collection.find_one({"employee_id": employee_id})
        
        if not employee:
            raise EmployeeNotFoundError(employee_id)
        
        logger.debug(f"Retrieved employee: {employee_id}")
        return Employee(**employee)

    async def update_employee(self, employee_id: str, employee_update: EmployeeUpdate) -> Employee:
        """
        Update employee by employee_id.
        
        Args:
            employee_id: Employee ID to update
            employee_update: Update data
            
        Returns:
            Employee: Updated employee object
            
        Raises:
            EmployeeNotFoundError: If employee not found
            ValidationError: If validation fails
        """
        # Check if employee exists
        existing_employee = await self.get_employee_by_id(employee_id)
        
        # Prepare update data (only include non-None fields)
        update_data = {k: v for k, v in employee_update.dict().items() if v is not None}
        
        if not update_data:
            raise ValidationError("No valid fields provided for update")
        
        # Validate update data
        await self.validate_document({**existing_employee.dict(), **update_data})
        
        # Update the employee
        collection = await self.get_collection()
        result = await collection.update_one(
            {"employee_id": employee_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise ValidationError("No changes made to the employee")
        
        # Return updated employee
        updated_employee = await self.get_employee_by_id(employee_id)
        
        logger.info(f"Updated employee: {employee_id}")
        return updated_employee

    async def delete_employee(self, employee_id: str) -> Dict[str, str]:
        """
        Delete employee by employee_id.
        
        Args:
            employee_id: Employee ID to delete
            
        Returns:
            Dict[str, str]: Success message
            
        Raises:
            EmployeeNotFoundError: If employee not found
        """
        # Check if employee exists
        await self.get_employee_by_id(employee_id)
        
        # Delete the employee
        collection = await self.get_collection()
        result = await collection.delete_one({"employee_id": employee_id})
        
        if result.deleted_count == 0:
            raise EmployeeNotFoundError(employee_id)
        
        logger.info(f"Deleted employee: {employee_id}")
        return {"message": f"Employee with ID {employee_id} deleted successfully"}

    async def get_employees_by_department(self, department: str, page: int = 1, page_size: int = 10) -> Tuple[List[Employee], PaginationMeta]:
        """
        Get employees by department with pagination, sorted by joining_date (newest first).
        
        Args:
            department: Department name to filter by
            page: Page number
            page_size: Number of items per page
            
        Returns:
            Tuple[List[Employee], PaginationMeta]: Employees and pagination metadata
        """
        # Count total items
        total_items = await self.count_documents({"department": department})
        
        # Calculate pagination
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
        skip = (page - 1) * page_size
        
        # Get paginated results
        employees = await self.find_documents(
            filter_dict={"department": department},
            skip=skip,
            limit=page_size,
            sort=[("joining_date", -1)]
        )
        
        # Create pagination metadata
        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        logger.debug(f"Retrieved {len(employees)} employees from department: {department}")
        return [Employee(**employee) for employee in employees], meta

    async def get_all_employees_paginated(self, page: int = 1, page_size: int = 10) -> Tuple[List[Employee], PaginationMeta]:
        """
        Get all employees with pagination, sorted by joining_date (newest first).
        
        Args:
            page: Page number
            page_size: Number of items per page
            
        Returns:
            Tuple[List[Employee], PaginationMeta]: Employees and pagination metadata
        """
        # Count total items
        total_items = await self.count_documents({})
        
        # Calculate pagination
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
        skip = (page - 1) * page_size
        
        # Get paginated results
        employees = await self.find_documents(
            skip=skip,
            limit=page_size,
            sort=[("joining_date", -1)]
        )
        
        # Create pagination metadata
        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        logger.debug(f"Retrieved {len(employees)} employees (page {page})")
        return [Employee(**employee) for employee in employees], meta

    async def search_employees_by_skill(self, skill: str, page: int = 1, page_size: int = 10) -> Tuple[List[Employee], PaginationMeta]:
        """
        Search employees by skill with pagination.
        
        Args:
            skill: Skill to search for
            page: Page number
            page_size: Number of items per page
            
        Returns:
            Tuple[List[Employee], PaginationMeta]: Employees and pagination metadata
        """
        # Count total items
        total_items = await self.count_documents({"skills": {"$regex": skill, "$options": "i"}})
        
        # Calculate pagination
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
        skip = (page - 1) * page_size
        
        # Get paginated results
        employees = await self.find_documents(
            filter_dict={"skills": {"$regex": skill, "$options": "i"}},
            skip=skip,
            limit=page_size
        )
        
        # Create pagination metadata
        meta = PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
        logger.debug(f"Found {len(employees)} employees with skill: {skill}")
        return [Employee(**employee) for employee in employees], meta

    async def get_average_salary_by_department(self) -> List[Dict[str, Any]]:
        """
        Get average salary by department using MongoDB aggregation.
        
        Returns:
            List[Dict[str, Any]]: Aggregated salary data by department
        """
        collection = await self.get_collection()
        
        pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "avg_salary": {"$avg": "$salary"}
                }
            },
            {
                "$project": {
                    "department": "$_id",
                    "avg_salary": {"$round": ["$avg_salary", 2]},
                    "_id": 0
                }
            },
            {
                "$sort": {"department": 1}
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        
        logger.debug(f"Retrieved salary aggregation for {len(result)} departments")
        return result

# Create a global instance
employee_service = EmployeeService()
