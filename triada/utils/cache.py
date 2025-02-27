from functools import lru_cache

class Cache:
    @lru_cache(maxsize=100)
    async def get_user_data(self, user_id: int) -> dict:
        # Получение данных пользователя с кэшированием
        pass 