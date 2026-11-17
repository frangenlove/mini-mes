class AppError(Exception):
    status_code = 400
    code = "BAD_REQUEST"
    def __init__(self,message: str):
        self.message = message

class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"

class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"

class UnauthorizedError(AppError):
    status_code=401
    code="UNAUTHORIZED"

class ForbiddenError(AppError):
    status_code=403
    code="FORBIDDEN"