from fastapi import APIRouter, status
from app.schemas.user import UserCreate, UserLogin, Token
from app.services.user_service import user_service

auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post(
    "/register", 
    status_code=status.HTTP_201_CREATED, 
    summary="Register a new user",
    description="Create a new user account to access protected employee management endpoints.",
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "username": "admin",
                        "id": "68c9fb64024287d83bd872ec"
                    }
                }
            }
        },
        400: {
            "description": "Username already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Username already registered"}
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
                                "loc": ["body", "username"],
                                "msg": "ensure this value has at least 3 characters",
                                "type": "value_error.any_str.min_length"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def register_user(user: UserCreate):
    """
    Register a new user account.
    
    This endpoint creates a new user account with the following features:
    - **Secure Password Storage**: Passwords are hashed using bcrypt
    - **Username Validation**: Ensures username is unique and meets requirements
    - **Account Creation**: Creates user account for accessing protected endpoints
    
    **Request Body:**
    - **username** (string, required): Username (3-50 characters, must be unique)
    - **password** (string, required): Password (minimum 6 characters)
    
    **Returns:**
    - User information including username and generated user ID
    - Returns 400 error if username already exists
    
    **Note:** After registration, use the login endpoint to get an access token.
    """
    return await user_service.create_user(user)

@auth_router.post(
    "/login", 
    response_model=Token, 
    summary="Login user",
    description="Authenticate user credentials and receive JWT access token for protected endpoints.",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
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
                                "loc": ["body", "username"],
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
async def login_user(user_login: UserLogin):
    """
    Login with username and password to get access token.
    
    This endpoint authenticates users and provides JWT tokens with the following features:
    - **Secure Authentication**: Validates username and password
    - **JWT Token Generation**: Returns secure access token
    - **Token Expiration**: Tokens expire after 30 minutes
    - **Bearer Authentication**: Use token in Authorization header
    
    **Request Body:**
    - **username** (string, required): Registered username
    - **password** (string, required): User password
    
    **Returns:**
    - JWT access token and token type
    - Returns 401 error for invalid credentials
    
    **Using the Token:**
    Include the token in the Authorization header for protected endpoints:
    ```
    Authorization: Bearer <your_access_token>
    ```
    
    **Token Expiration:**
    - Tokens expire after 30 minutes
    - Re-authenticate using this endpoint to get a new token
    """
    return await user_service.login_for_access_token(user_login)
