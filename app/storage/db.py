import aiosqlite
from app.config import Config
from loguru import logger


class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn = None

    async def connect(self):
        logger.info(f"Подключение к базе данных: {self.path}")
        self._conn = await aiosqlite.connect(self.path)
        await self._conn.execute("PRAGMA foreign_keys = ON;")
        await self.migrate()

    async def migrate(self):
        logger.info("Проверка и создание таблиц (миграция)...")

        await self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS votes (
                user_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                value INTEGER NOT NULL CHECK(value IN (1, -1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, challenge_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS saved (
                user_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, challenge_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
            );
            """
        )
        await self._conn.commit()
        logger.success("Миграция завершена ✅")

    async def execute(self, query: str, params: tuple = ()):
        cursor = await self._conn.execute(query, params)
        await self._conn.commit()
        return cursor

    async def fetchone(self, query: str, params: tuple = ()):
        cursor = await self._conn.execute(query, params)
        row = await cursor.fetchone()
        return row

    async def fetchall(self, query: str, params: tuple = ()):
        cursor = await self._conn.execute(query, params)
        rows = await cursor.fetchall()
        return rows
