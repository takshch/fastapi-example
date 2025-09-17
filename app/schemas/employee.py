from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: any, handler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class EmployeeBase(BaseModel):
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Employee's full name",
        example="John Doe"
    )
    department: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Department name",
        example="Engineering"
    )
    salary: float = Field(
        ..., 
        gt=0, 
        description="Annual salary in USD",
        example=75000.0
    )
    joining_date: str = Field(
        ..., 
        description="Joining date in YYYY-MM-DD format",
        example="2023-01-15"
    )
    skills: List[str] = Field(
        ..., 
        min_items=1, 
        description="List of employee skills",
        example=["Python", "MongoDB", "APIs"]
    )

class EmployeeWithId(EmployeeBase):
    employee_id: str = Field(
        ..., 
        description="Unique employee identifier (auto-generated)",
        example="E001"
    )

    @field_validator('joining_date')
    @classmethod
    def validate_joining_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('joining_date must be in YYYY-MM-DD format')

    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one skill is required')
        return [skill.strip() for skill in v if skill.strip()]

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100,
        description="Employee's full name",
        example="John Doe"
    )
    department: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=50,
        description="Department name",
        example="Engineering"
    )
    salary: Optional[float] = Field(
        None, 
        gt=0,
        description="Annual salary in USD",
        example=80000.0
    )
    joining_date: Optional[str] = Field(
        None,
        description="Joining date in YYYY-MM-DD format",
        example="2023-01-15"
    )
    skills: Optional[List[str]] = Field(
        None, 
        min_items=1,
        description="List of employee skills",
        example=["Python", "MongoDB", "APIs", "Docker"]
    )

    @field_validator('joining_date')
    @classmethod
    def validate_joining_date(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('joining_date must be in YYYY-MM-DD format')
        return v

    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v):
        if v is not None:
            if len(v) == 0:
                raise ValueError('At least one skill is required')
            return [skill.strip() for skill in v if skill.strip()]
        return v

class Employee(EmployeeWithId):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EmployeeResponse(BaseModel):
    id: str = Field(
        ..., 
        description="Employee ID (auto-generated)",
        example="E001"
    )
    name: str = Field(
        ...,
        description="Employee's full name",
        example="John Doe"
    )
    department: str = Field(
        ...,
        description="Department name",
        example="Engineering"
    )
    salary: float = Field(
        ...,
        description="Annual salary in USD",
        example=75000.0
    )
    joining_date: str = Field(
        ...,
        description="Joining date in YYYY-MM-DD format",
        example="2023-01-15"
    )
    skills: List[str] = Field(
        ...,
        description="List of employee skills",
        example=["Python", "MongoDB", "APIs"]
    )

    class Config:
        from_attributes = True
