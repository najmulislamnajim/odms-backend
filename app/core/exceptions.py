class AppError(Exception):
    """Base error raised by services; mapped to an HTTP response in main.py.
    
    Services raise these instead of HTTPException so they stay usable outside
    a web request (Celery jobs, admin scripts, tests).
    """
    
    status_code: int = 400 
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
        
class BadRequestError(AppError):
    status_code = 400
    
class NotFoundError(AppError):
    status_code = 404
    
class ConflictError(AppError):
    """The action clashes with the current state, e.g. already delivered."""
    
    status_code = 409
    
class BusinessRuleError(AppError):
    """The input is well formed but breaks a business rule."""
    
    status_code = 422 
    