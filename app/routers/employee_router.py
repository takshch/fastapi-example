from fastapi import APIRouter

employee_router = APIRouter(prefix="/employees", tags=["employees"])

@employee_router.post('/', summary="Create a new employee")
async def create_employee(employee: dict):
    """Create a new employee"""
    return {"message": "Employee created", "employee": employee}

@employee_router.patch('/{employee_id}', summary="Update an existing employee")
async def update_employee(employee_id: int, employee: dict):
    """Update an existing employee"""
    return {"message": "Employee updated", "employee_id": employee_id, "employee": employee}

@employee_router.delete('/{employee_id}', summary="Delete an employee")
async def delete_employee(employee_id: int):
    """Delete an employee"""
    return {"message": "Employee deleted", "employee_id": employee_id}

@employee_router.get('/{employee_id}', summary="Get an employee by ID")
async def get_employee(employee_id: int):           
    """Get an employee by ID"""
    return {"employee_id": employee_id, "name": "John Doe", "position": "Developer"}

