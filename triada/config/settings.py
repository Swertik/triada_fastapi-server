import os
from dotenv import load_dotenv

load_dotenv()

# GROUP_TOKEN = os.getenv('GROUP_TOKEN')
# MY_TOKEN = os.getenv('MY_TOKEN')
# DATABASE_URL = os.getenv('DATABASE_URL')
# TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')
# REDIS_HOST = 'localhost'
# Раскомментировать перед пушем
GROUP_TOKEN = open("/run/secrets/group_token").read().strip()
MY_TOKEN = open("/run/secrets/my_token").read().strip()
DATABASE_URL = open("/run/secrets/database_udl").read().strip
TEST_DATABASE_URL = open("/run/secrets/database_udl").read().strip
REDIS_HOST = 'redis'
GROUP_ID = 229144827
JUDGE_CHAT_ID = 2000000002
FLOOD_CHAT_ID = 2000000001

