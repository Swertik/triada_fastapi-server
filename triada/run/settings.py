import os
def read_secret(filepath):
    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None  # Не падаем с ошибкой

GROUP_TOKEN = read_secret("secrets/group_token")
MY_TOKEN = read_secret("secrets/my_token")
DATABASE_URL = read_secret("secrets/database_url")
TEST_DATABASE_URL = read_secret("secrets/test_database_url")
REDIS_HOST = 'redis'
GROUP_ID = 229144827
JUDGE_CHAT_ID = 2000000002
FLOOD_CHAT_ID = 2000000001

print(GROUP_TOKEN)
print(MY_TOKEN)
print(DATABASE_URL)