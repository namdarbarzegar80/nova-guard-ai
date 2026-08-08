import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

DATABASE_PATH = "nova_guard.db"

BOT_NAME = "Nova Guard AI"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
