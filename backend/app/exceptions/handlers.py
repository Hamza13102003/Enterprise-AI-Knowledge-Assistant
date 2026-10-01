from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import EnterpriseAIException
from app.schemas.error_response import ErrorDetail, ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers.
    """

    @app.exception_handler(EnterpriseAIException)
    async def enterprise_exception_handler(
        request: Request,
        exc: EnterpriseAIException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=exc.error_code,
                    message=exc.message,
                )
            ).model_dump(),
        )
