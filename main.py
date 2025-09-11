from fastapi import FastAPI, status
from app.routers.employee_router import employee_router
from app.errors.exception_handlers import (
    not_found_error_handler,
    server_error_handler,
)

app = FastAPI()

app.include_router(employee_router)

app.add_exception_handler(status.HTTP_404_NOT_FOUND, not_found_error_handler)
app.add_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, server_error_handler)
