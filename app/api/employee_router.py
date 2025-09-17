from fastapi import APIRouter, Query, HTTPException, status, Depends
from typing import List, Optional, Union
from app.schemas.employee import Employee, EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.services.employee_service import employee_service
from app.auth import get_current_user

employee_router = APIRouter(prefix="/employees", tags=["employees"])

@employee_router.post(
    '', 
    response_model=EmployeeResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a new employee",
    description="Create a new employee record with auto-generated employee ID. Requires JWT authentication.",
    responses={
        201: {
            "description": "Employee created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "E001",
                        "name": "John Doe",
                        "department": "Engineering",
                        "salary": 75000.0,
                        "joining_date": "2023-01-15",
                        "skills": ["Python", "MongoDB", "APIs"]
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "name"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_employee(employee: EmployeeCreate, current_user: dict = Depends(get_current_user)):
    """
    Create a new employee record.
    
    This endpoint creates a new employee with the following features:
    - **Auto-generated ID**: Employee ID is automatically generated in sequence (E001, E002, E003, etc.)
    - **Data Validation**: All fields are validated according to business rules
    - **Authentication Required**: JWT token must be provided in Authorization header
    
    **Request Body:**
    - **name** (string, required): Employee's full name (1-100 characters)
    - **department** (string, required): Department name (1-50 characters)
    - **salary** (number, required): Annual salary (must be positive)
    - **joining_date** (string, required): Joining date in YYYY-MM-DD format
    - **skills** (array, required): List of employee skills (at least one skill required)
    
    **Authentication:**
    Include JWT token in Authorization header: `Bearer <your_token>`
    """
    created_employee = await employee_service.create_employee(employee)
    return EmployeeResponse(
        id=created_employee.employee_id,                                                                                                                                                                                                                                
        name=created_employee.name,
        department=created_employee.department,
        salary=created_employee.salary,
        joining_date=created_employee.joining_date,
        skills=created_employee.skills
    )


@employee_router.put(
    '/{employee_id}', 
    response_model=EmployeeResponse, 
    summary="Update an employee",
    description="Update employee information. Supports partial updates - only provided fields will be updated.",
    responses={
        200: {
            "description": "Employee updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "E001",
                        "name": "John Doe",
                        "department": "Engineering",
                        "salary": 80000.0,
                        "joining_date": "2023-01-15",
                        "skills": ["Python", "MongoDB", "APIs", "Docker"]
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        404: {
            "description": "Employee not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Employee with ID E999 not found"}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "salary"],
                                "msg": "ensure this value is greater than 0",
                                "type": "value_error.number.not_gt"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def update_employee(employee_id: str, employee_update: EmployeeUpdate, current_user: dict = Depends(get_current_user)):
    """
    Update employee details.
    
    This endpoint allows you to update employee information with the following features:
    - **Partial Updates**: Only provide the fields you want to update
    - **Data Validation**: All provided fields are validated
    - **Authentication Required**: JWT token must be provided
    
    **Parameters:**
    - **employee_id** (string, path): The unique employee identifier to update
    
    **Request Body (all fields optional):**
    - **name** (string): Employee's full name (1-100 characters)
    - **department** (string): Department name (1-50 characters)
    - **salary** (number): Annual salary (must be positive)
    - **joining_date** (string): Joining date in YYYY-MM-DD format
    - **skills** (array): List of employee skills (at least one skill if provided)
    
    **Authentication:**
    Include JWT token in Authorization header: `Bearer <your_token>`
    
    **Example Partial Update:**
    ```json
    {
        "salary": 80000,
        "skills": ["Python", "MongoDB", "APIs", "Docker"]
    }
    ```
    """
    updated_employee = await employee_service.update_employee(employee_id, employee_update)
    return EmployeeResponse(
        id=updated_employee.employee_id,
        name=updated_employee.name,
        department=updated_employee.department,
        salary=updated_employee.salary,
        joining_date=updated_employee.joining_date,
        skills=updated_employee.skills
    )

@employee_router.delete(
    '/{employee_id}', 
    summary="Delete an employee",
    description="Permanently delete an employee record from the system.",
    responses={
        200: {
            "description": "Employee deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Employee with ID E001 deleted successfully"}
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        404: {
            "description": "Employee not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Employee with ID E999 not found"}
                }
            }
        }
    }
)
async def delete_employee(employee_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete employee record.
    
    This endpoint permanently removes an employee from the system.
    
    **Parameters:**
    - **employee_id** (string, path): The unique employee identifier to delete
    
    **Returns:**
    - Success message confirming deletion
    - Returns 404 error if employee with the specified ID is not found
    
    **Authentication:**
    Include JWT token in Authorization header: `Bearer <your_token>`
    
    **Warning:** This action is irreversible. The employee record will be permanently deleted.
    """
    result = await employee_service.delete_employee(employee_id)
    return result

@employee_router.get(
    '', 
    response_model=Union[List[EmployeeResponse], PaginatedResponse[EmployeeResponse]], 
    summary="List employees by department",
    description="Retrieve a list of employees, optionally filtered by department. Results are sorted by joining date (newest first). Supports pagination.",
    responses={
        200: {
            "description": "List of employees retrieved successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "without_pagination": {
                            "summary": "Without pagination",
                            "value": [
                                {
                                    "id": "E002",
                                    "name": "Jane Smith",
                                    "department": "Engineering",
                                    "salary": 85000.0,
                                    "joining_date": "2023-02-20",
                                    "skills": ["JavaScript", "React", "Node.js"]
                                },
                                {
                                    "id": "E001",
                                    "name": "John Doe",
                                    "department": "Engineering",
                                    "salary": 75000.0,
                                    "joining_date": "2023-01-15",
                                    "skills": ["Python", "MongoDB", "APIs"]
                                }
                            ]
                        },
                        "with_pagination": {
                            "summary": "With pagination",
                            "value": {
                                "items": [
                                    {
                                        "id": "E002",
                                        "name": "Jane Smith",
                                        "department": "Engineering",
                                        "salary": 85000.0,
                                        "joining_date": "2023-02-20",
                                        "skills": ["JavaScript", "React", "Node.js"]
                                    }
                                ],
                                "meta": {
                                    "page": 1,
                                    "page_size": 10,
                                    "total_items": 25,
                                    "total_pages": 3,
                                    "has_next": True,
                                    "has_previous": False
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def list_employees_by_department(
    department: Optional[str] = Query(None, description="Filter by department name (e.g., 'Engineering', 'HR', 'Marketing')"),
    page: Optional[int] = Query(None, ge=1, description="Page number for pagination (starts from 1)"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Number of items per page (max 100)")
):
    """
    Return employees in a department, sorted by joining_date (newest first).
    
    This endpoint provides flexible employee listing with the following features:
    - **Department Filtering**: Optionally filter employees by department
    - **Sorted Results**: Employees are sorted by joining date (newest first)
    - **Pagination Support**: Optional pagination with page and page_size parameters
    - **Public Access**: No authentication required
    
    **Query Parameters:**
    - **department** (string, optional): Department name to filter by
    - **page** (integer, optional): Page number for pagination (starts from 1)
    - **page_size** (integer, optional): Number of items per page (max 100)
    
    **Examples:**
    - Get all employees: `GET /employees`
    - Get Engineering employees: `GET /employees?department=Engineering`
    - Get paginated results: `GET /employees?page=1&page_size=5`
    - Get paginated Engineering employees: `GET /employees?department=Engineering&page=1&page_size=5`
    
    **Returns:**
    - If pagination parameters provided: Paginated response with items and metadata
    - If no pagination parameters: Array of employee objects
    - Empty array/response if no employees found for the specified department
    """
    # Check if pagination is requested
    use_pagination = page is not None or page_size is not None
    
    if use_pagination:
        # Set default values if only one pagination parameter is provided
        page = page or 1
        page_size = page_size or 10
        
        if department:
            employees, meta = await employee_service.get_employees_by_department(department, page, page_size)
        else:
            employees, meta = await employee_service.get_all_employees_paginated(page, page_size)
        
        return PaginatedResponse(
            items=[
                EmployeeResponse(
                    id=emp.employee_id,
                    name=emp.name,
                    department=emp.department,
                    salary=emp.salary,
                    joining_date=emp.joining_date,
                    skills=emp.skills
                ) for emp in employees
            ],
            meta=meta
        )
    else:
        # Legacy behavior without pagination
        if department:
            employees, _ = await employee_service.get_employees_by_department(department)
        else:
            employees, _ = await employee_service.get_all_employees_paginated()
        
        return [
            EmployeeResponse(
                id=emp.employee_id,
                name=emp.name,
                department=emp.department,
                salary=emp.salary,
                joining_date=emp.joining_date,
                skills=emp.skills
            ) for emp in employees
        ]

@employee_router.get(
    '/avg-salary', 
    summary="Average salary by department",
    description="Calculate the average salary for each department using MongoDB aggregation pipeline.",
    responses={
        200: {
            "description": "Average salary data retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "department": "Engineering",
                            "avg_salary": 82500.0
                        },
                        {
                            "department": "HR",
                            "avg_salary": 62500.0
                        },
                        {
                            "department": "Marketing",
                            "avg_salary": 56500.0
                        }
                    ]
                }
            }
        }
    }
)
async def get_average_salary_by_department():
    """
    Use MongoDB aggregation to compute average salary grouped by department.
    
    This endpoint provides salary analytics with the following features:
    - **MongoDB Aggregation**: Uses advanced aggregation pipeline for calculations
    - **Department Grouping**: Groups employees by department
    - **Average Calculation**: Computes average salary for each department
    - **Sorted Results**: Results are sorted alphabetically by department name
    - **Public Access**: No authentication required
    
    **Returns:**
    - Array of objects containing department name and average salary
    - Average salary is rounded to 2 decimal places
    - Empty array if no employees exist in the system
    
    **Use Cases:**
    - Salary benchmarking across departments
    - Budget planning and analysis
    - HR reporting and analytics
    """
    result = await employee_service.get_average_salary_by_department()
    return result

@employee_router.get(
    '/search', 
    response_model=Union[List[EmployeeResponse], PaginatedResponse[EmployeeResponse]], 
    summary="Search employees by skill",
    description="Find employees who have a specific skill. Search is case-insensitive and supports partial matching. Supports pagination.",
    responses={
        200: {
            "description": "Employees with the specified skill found",
            "content": {
                "application/json": {
                    "examples": {
                        "without_pagination": {
                            "summary": "Without pagination",
                            "value": [
                                {
                                    "id": "E001",
                                    "name": "John Doe",
                                    "department": "Engineering",
                                    "salary": 75000.0,
                                    "joining_date": "2023-01-15",
                                    "skills": ["Python", "MongoDB", "APIs"]
                                },
                                {
                                    "id": "E004",
                                    "name": "Sarah Wilson",
                                    "department": "Engineering",
                                    "salary": 90000.0,
                                    "joining_date": "2023-04-05",
                                    "skills": ["Python", "Docker", "Kubernetes", "AWS"]
                                }
                            ]
                        },
                        "with_pagination": {
                            "summary": "With pagination",
                            "value": {
                                "items": [
                                    {
                                        "id": "E001",
                                        "name": "John Doe",
                                        "department": "Engineering",
                                        "salary": 75000.0,
                                        "joining_date": "2023-01-15",
                                        "skills": ["Python", "MongoDB", "APIs"]
                                    }
                                ],
                                "meta": {
                                    "page": 1,
                                    "page_size": 10,
                                    "total_items": 15,
                                    "total_pages": 2,
                                    "has_next": True,
                                    "has_previous": False
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def search_employees_by_skill(
    skill: str = Query(..., description="Skill name to search for (e.g., 'Python', 'JavaScript', 'Docker')"),
    page: Optional[int] = Query(None, ge=1, description="Page number for pagination (starts from 1)"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Number of items per page (max 100)")
):
    """
    Search employees by skill.
    
    This endpoint allows you to find employees based on their skills with the following features:
    - **Case-Insensitive Search**: Search is not case-sensitive
    - **Partial Matching**: Supports partial skill name matching
    - **Pagination Support**: Optional pagination with page and page_size parameters
    - **Public Access**: No authentication required
    
    **Query Parameters:**
    - **skill** (string, required): Skill name to search for
    - **page** (integer, optional): Page number for pagination (starts from 1)
    - **page_size** (integer, optional): Number of items per page (max 100)
    
    **Examples:**
    - Find Python developers: `GET /employees/search?skill=Python`
    - Find JavaScript developers: `GET /employees/search?skill=JavaScript`
    - Find Docker users: `GET /employees/search?skill=Docker`
    - Find Python developers with pagination: `GET /employees/search?skill=Python&page=1&page_size=5`
    
    **Returns:**
    - If pagination parameters provided: Paginated response with items and metadata
    - If no pagination parameters: Array of employee objects who have the specified skill
    - Empty array/response if no employees found with the specified skill
    
    **Note:** The search will match any employee whose skills array contains the specified skill (case-insensitive).
    """
    # Check if pagination is requested
    use_pagination = page is not None or page_size is not None
    
    if use_pagination:
        # Set default values if only one pagination parameter is provided
        page = page or 1
        page_size = page_size or 10
        
        employees, meta = await employee_service.search_employees_by_skill(skill, page, page_size)
        
        return PaginatedResponse(
            items=[
                EmployeeResponse(
                    id=emp.employee_id,
                    name=emp.name,
                    department=emp.department,
                    salary=emp.salary,
                    joining_date=emp.joining_date,
                    skills=emp.skills
                ) for emp in employees
            ],
            meta=meta
        )
    else:
        # Legacy behavior without pagination
        employees, _ = await employee_service.search_employees_by_skill(skill)
        
        return [
            EmployeeResponse(
                id=emp.employee_id,
                name=emp.name,
                department=emp.department,
                salary=emp.salary,
                joining_date=emp.joining_date,
                skills=emp.skills
            ) for emp in employees
        ]

@employee_router.get(
    '/{employee_id}', 
    response_model=EmployeeResponse, 
    summary="Get an employee by ID",
    description="Retrieve detailed information about a specific employee using their employee ID.",
    responses={
        200: {
            "description": "Employee found successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "E001",
                        "name": "John Doe",
                        "department": "Engineering",
                        "salary": 75000.0,
                        "joining_date": "2023-01-15",
                        "skills": ["Python", "MongoDB", "APIs"]
                    }
                }
            }
        },
        404: {
            "description": "Employee not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Employee with ID E999 not found"}
                }
            }
        }
    }
)
async def get_employee(employee_id: str):
    """
    Fetch employee details by employee ID.
    
    This endpoint retrieves complete information about a specific employee.
    
    **Parameters:**
    - **employee_id** (string, path): The unique employee identifier (e.g., E001, E002, etc.)
    
    **Returns:**
    - Complete employee information including ID, name, department, salary, joining date, and skills
    - Returns 404 error if employee with the specified ID is not found
    
    **Note:** This is a public endpoint and does not require authentication.
    """
    employee = await employee_service.get_employee_by_id(employee_id)
    return EmployeeResponse(
        id=employee.employee_id,
        name=employee.name,
        department=employee.department,
        salary=employee.salary,
        joining_date=employee.joining_date,
        skills=employee.skills
    )

