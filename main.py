"""
Main FastAPI application entry point.

This module creates and configures the FastAPI application with all
necessary middleware, routers, and exception handlers.
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.logging import setup_logging, RequestLoggingMiddleware
from app.core.exceptions import BaseAPIException
from app.api.employee_router import employee_router
from app.api.auth_router import auth_router
from app.errors.exception_handlers import (
    base_api_exception_handler,
    http_exception_handler,
    not_found_error_handler,
    server_error_handler,
    validation_error_handler,
)
from app.database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")
    
    try:
        await connect_to_mongo()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_mongo_connection()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    # Setup logging
    setup_logging()
    
    app = FastAPI(
        title=settings.app_name,
        description="""
        ## Employee Management System
        
        A comprehensive FastAPI application for managing employee records with MongoDB integration.
        
        ### Features
        - **CRUD Operations**: Create, Read, Update, Delete employee records
        - **JWT Authentication**: Secure authentication for Create, Update, Delete operations
        - **Advanced Querying**: Filter by department, search by skills
        - **Pagination**: Optional pagination for large datasets
        - **Aggregation**: Average salary by department using MongoDB aggregation
        - **Data Validation**: Comprehensive input validation using Pydantic
        - **Auto-generated IDs**: Employee IDs are automatically generated (E001, E002, etc.)
        
        ### Authentication
        - Register a new user account using `/auth/register`
        - Login to get JWT token using `/auth/login`
        - Use the token in Authorization header: `Bearer <your_token>`
        
        ### Protected Endpoints
        - `POST /employees` - Create employee (requires authentication)
        - `PUT /employees/{id}` - Update employee (requires authentication)
        - `DELETE /employees/{id}` - Delete employee (requires authentication)
        
        ### Public Endpoints
        - `GET /employees` - List all employees
        - `GET /employees/{id}` - Get employee by ID
        - `GET /employees/search` - Search employees by skill
        - `GET /employees/avg-salary` - Get average salary by department
        """,
        version=settings.app_version,
        lifespan=lifespan,
        contact={
            "name": "API Support",
            "email": "support@example.com",
        },
        license_info={
            "name": "MIT",
        },
        servers=[
            {
                "url": f"http://{settings.host}:{settings.port}",
                "description": f"{settings.environment.title()} server"
            }
        ]
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(employee_router)
    
    # Add exception handlers
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(status.HTTP_404_NOT_FOUND, not_found_error_handler)
    app.add_exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY, validation_error_handler)
    app.add_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, server_error_handler)
    
    return app


# Create the application instance
app = create_app()


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint"""
    return {"message": "Employee Management API is running!"}


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check endpoint"""
    from app.database import db_manager
    
    db_healthy = await db_manager.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.app_version,
        "environment": settings.environment
    }
