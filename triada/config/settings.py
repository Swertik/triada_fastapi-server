import os
from dotenv import load_dotenv

load_dotenv()

def read_secret(env_var):
    filepath = os.getenv(env_var)
    """Читает секрет из файла или переменной окружения"""
    if os.path.exists(filepath):  # Если файл есть — читаем из файла
        with open(filepath, "r") as f:
            return f.read().strip()
    return False  # Иначе читаем из ENV (например, для локальных тестов)



GROUP_TOKEN = read_secret(f"GROUP_TOKEN_FILE")
MY_TOKEN = read_secret(f"MY_TOKEN_FILE")
DATABASE_URL = read_secret("DATABASE_URL_FILE")
REDIS_HOST = os.getenv(f"REDIS_HOST")
GROUP_ID = 229144827
JUDGE_CHAT_ID = 2000000002
FLOOD_CHAT_ID = 2000000001

if __name__ == "__main__":
    while True:

        directory = input('Введи директорию ')
        contents = os.listdir(directory)
        print(f"Содержимое директории {directory}:")
        for item in contents:
            print(item)