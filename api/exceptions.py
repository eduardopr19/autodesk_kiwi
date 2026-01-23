from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from logger import setup_logger

logger = setup_logger("exceptions")


class AppException(Exception):
    """Exception de base de l'app"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class TaskNotFoundException(AppException):
    def __init__(self, task_id: int):
        super().__init__(f"Task {task_id} not found", 404)


class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__(message, 400)


async def app_exception_handler(request: Request, exc: AppException):
    """Handler pour exceptions custom"""
    logger.error(f"{exc.__class__.__name__}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": exc.__class__.__name__}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler pour exceptions génériques"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "InternalServerError"}
    )