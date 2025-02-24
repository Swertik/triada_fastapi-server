class TriadaException(Exception):
    """Базовое исключение для приложения"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)

class VkApiError(TriadaException):
    """Ошибка при работе с VK API"""
    pass

class DatabaseError(TriadaException):
    """Ошибка при работе с базой данных"""
    pass 