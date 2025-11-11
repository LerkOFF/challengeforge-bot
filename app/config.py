from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise RuntimeError("❌ BOT_TOKEN не найден. Добавьте его в .env")
