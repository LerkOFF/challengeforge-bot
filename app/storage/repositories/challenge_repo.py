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

    async def get_top_by_score(self, limit: int = 10) -> List[Tuple[int, str, int]]:
        rows = await self.db.fetchall(
            """
            SELECT c.id, c.title, COALESCE(SUM(v.value), 0) AS score
            FROM challenges c
            LEFT JOIN votes v ON v.challenge_id = c.id
            GROUP BY c.id
            ORDER BY score DESC, c.id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return rows

    async def get_by_id(self, challenge_id: int):
        return await self.db.fetchone(
            "SELECT id, title, body, tags FROM challenges WHERE id = ?",
            (challenge_id,),
        )
