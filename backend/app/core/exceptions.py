from collections.abc import Sequence


class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        details: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = list(details or [])


class AzureIntegrationError(AppError):
    def __init__(self, message: str, *, details: Sequence[str] | None = None) -> None:
        super().__init__(message, status_code=502, details=details)


class NotFoundError(AppError):
    def __init__(self, message: str, *, details: Sequence[str] | None = None) -> None:
        super().__init__(message, status_code=404, details=details)
