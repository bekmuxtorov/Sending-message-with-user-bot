from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")

API_HASH = env.str("API_HASH")
API_ID = env.int("API_ID")

DEFAULT_CODE_OFFSET = env.int("DEFAULT_CODE_OFFSET", 1)
FILTER_NAME = "Avto"

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")

TIME_BETWEEN_MESSAGE = [2, 4, 6, 8, 10, 15, 20, 30, 45, 60]
UZ_TIMEZONE = "Asia/Tashkent"

SAVE_GROUP_ID = env.str("SAVE_GROUP_ID")
SAVE_MESSAGE_TOPIC_ID = env.int("SAVE_MESSAGE_TOPIC_ID")
