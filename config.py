import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
FIREBASE_KEY_PATH: str = os.getenv("FIREBASE_KEY_PATH", "firebase_key.json")

# Список ID адміністраторів у Telegram (через кому в .env або дефолтний список)
admin_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = [int(x.strip()) for x in admin_raw.split(",") if x.strip().isdigit()]