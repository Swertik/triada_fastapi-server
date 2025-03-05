import os
from dotenv import load_dotenv

load_dotenv()

GROUP_TOKEN = os.getenv('GROUP_TOKEN')
MY_TOKEN = os.getenv('MY_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
GROUP_ID = 229144827
JUDGE_CHAT_ID = 2000000002
FLOOD_CHAT_ID = 2000000001

