from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status


async def not_found_error_handler(request: Request, exc: Exception):
  return JSONResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    content={"message": "Resource not found"},
  )


async def server_error_handler(request: Request, exc: Exception):
  return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={"message": "Internal server error"},
  )
