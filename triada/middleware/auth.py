from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from triada.utils.exceptions import TriadaException

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not self._is_valid_token(request):
            raise TriadaException("Invalid token", 401)
        response = await call_next(request)
        return response

    def _is_valid_token(self, request):
        pass
    #TODO: Добавить проверку вк-токена, скорее всего через http запрос