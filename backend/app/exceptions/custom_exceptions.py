from fastapi import status


class EnterpriseAIException(Exception):
    """
    Base exception for the Enterprise AI Knowledge Assistant.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundException(EnterpriseAIException):
    """
    Raised when a requested resource cannot be found.
    """

    def __init__(
        self,
        resource: str,
        resource_id: str,
    ) -> None:
        super().__init__(
            message=f"{resource} with ID '{resource_id}' was not found.",
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationException(EnterpriseAIException):
    """
    Raised when request validation fails.
    """

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class AuthenticationException(EnterpriseAIException):
    """
    Raised when authentication fails.
    """

    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class DocumentProcessingException(EnterpriseAIException):
    """
    Raised when document processing fails.
    """

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            error_code="DOCUMENT_PROCESSING_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
