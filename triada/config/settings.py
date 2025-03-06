import os
from dotenv import load_dotenv

load_dotenv()

import os
import dotenv

def read_secret(filepath, env_var):
    """Читает секрет из файла или переменной окружения"""
    if os.path.exists(filepath):  # Если файл есть — читаем из файла
        with open(filepath, "r") as f:
            return f.read().strip()
    return os.getenv(env_var)  # Иначе читаем из ENV (например, для локальных тестов)

# Универсальный путь для Docker, CI/CD и локальных тестов
SECRETS_PATH = "/run/secrets" if os.path.exists("/run/secrets") else "/tmp/secrets"

GROUP_TOKEN = read_secret(f"{SECRETS_PATH}/group_token", "GROUP_TOKEN")
MY_TOKEN = read_secret(f"{SECRETS_PATH}/my_token", "MY_TOKEN")
DATABASE_URL = read_secret(f"{SECRETS_PATH}/database_url", "DATABASE_URL")
TEST_DATABASE_URL = read_secret(f"{SECRETS_PATH}/test_database_url", "TEST_DATABASE_URL")
REDIS_HOST = 'redis'
GROUP_ID = 229144827
JUDGE_CHAT_ID = 2000000002
FLOOD_CHAT_ID = 2000000001