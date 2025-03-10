import os
from dotenv import load_dotenv

load_dotenv()

def read_secret(env_var, test_env_var):
    filepath = os.getenv(env_var)
    """Читает секрет из файла или переменной окружения"""
    try:
        if os.path.exists(filepath):  # Если файл есть — читаем из файла
            with open(filepath, "r") as f:
                return f.read().strip()
    except:
        pass
    return os.getenv(test_env_var)  # Иначе читаем из ENV (например, для локальных тестов)



GROUP_TOKEN = read_secret("GROUP_TOKEN_FILE", "GROUP_TOKEN")
MY_TOKEN = read_secret("MY_TOKEN_FILE", "MY_TOKEN")
DATABASE_URL = read_secret("DATABASE_URL_FILE", "DATABASE_URL")
TEST_DATABASE_URL = read_secret("TEST_DATABASE_URL_FILE", "TEST_DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST")
GROUP_ID = 229144827
JUDGE_CHAT_ID = 2000000002
FLOOD_CHAT_ID = 2000000001

if __name__ == "__main__":
    print(TEST_DATABASE_URL)