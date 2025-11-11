from typing import Optional, Tuple, List


class ChallengeRepo:
    def __init__(self, db):
        self.db = db

    async def create(self, title: str, body: str, tags: str) -> int:
        cursor = await self.db.execute(
            "INSERT INTO challenges (title, body, tags) VALUES (?, ?, ?)",
            (title, body, tags)
        )
        return cursor.lastrowid

    async def get_random(self) -> Optional[Tuple[int, str, str, str]]:
        row = await self.db.fetchone(
            "SELECT id, title, body, tags FROM challenges ORDER BY RANDOM() LIMIT 1"
        )
        return row

    async def get_by_title_body(self, title: str, body: str) -> Optional[Tuple[int, str, str, str]]:
        row = await self.db.fetchone(
            "SELECT id, title, body, tags FROM challenges WHERE title = ? AND body = ? LIMIT 1",
            (title, body),
        )
        return row

    async def get_top(self, limit: int = 10) -> List[Tuple[int, str, str, str]]:
        # пригодится позже
        rows = await self.db.fetchall(
            "SELECT id, title, body, tags FROM challenges ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return rows
