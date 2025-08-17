from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")

API_HASH = env.str("API_HASH")
API_ID = env.int("API_ID")

DEFAULT_CODE_OFFSET = env.int("DEFAULT_CODE_OFFSET", 1)

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")
