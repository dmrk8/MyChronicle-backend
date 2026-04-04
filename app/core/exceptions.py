from fastapi import status

class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)

class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)

class ConflictException(AppException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status.HTTP_409_CONFLICT, detail)
        
class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)

def _resolve_status_code(upstream_code: int) -> int:
    return {
        429: 429,  # rate limit — client should back off
        404: 404,  # not found — valid to forward
        401: 503,  # their auth issue — not client's fault, hide it
        403: 503,  # same
        500: 503,  # their internal error → your service unavailable
    }.get(upstream_code, 503)  # default everything else to 503

class UpstreamServiceException(AppException):
    def __init__(self, service_name: str, upstream_status_code: int = 503):
        super().__init__(
            status_code=_resolve_status_code(upstream_status_code),
            detail=f"{service_name} is currently unavailable. Please try again later."
        )
        
class AuthenticationError(AppException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)
               