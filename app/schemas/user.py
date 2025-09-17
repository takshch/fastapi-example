from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="Username (must be unique)",
        example="admin"
    )
    password: str = Field(
        ..., 
        min_length=6, 
        description="Password (minimum 6 characters)",
        example="admin123"
    )

class UserLogin(BaseModel):
    username: str = Field(
        ..., 
        description="Username",
        example="admin"
    )
    password: str = Field(
        ..., 
        description="Password",
        example="admin123"
    )

class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT access token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: str = Field(
        ...,
        description="Token type",
        example="bearer"
    )

class TokenData(BaseModel):
    username: Optional[str] = None
