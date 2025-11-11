from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DB_PATH = os.getenv("DB_PATH", "database.db")
    CALLBACK_SECRET = os.getenv("CALLBACK_SECRET", "")

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise RuntimeError("❌ BOT_TOKEN не найден в .env")
