class SavedRepo:
    def __init__(self, db):
        self.db = db

    async def save(self, user_id: int, challenge_id: int):
        await self.db.execute(
            """
            INSERT INTO saved (user_id, challenge_id)
            VALUES (?, ?)
            ON CONFLICT(user_id, challenge_id) DO NOTHING
            """,
            (user_id, challenge_id),
        )

    async def list_for_user(self, user_id: int, limit: int = 10):
        rows = await self.db.fetchall(
            """
            SELECT c.id, c.title, COALESCE(SUM(v.value), 0) AS score
            FROM saved s
            JOIN challenges c ON c.id = s.challenge_id
            LEFT JOIN votes v ON v.challenge_id = c.id
            WHERE s.user_id = ?
            GROUP BY c.id
            ORDER BY s.created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        return rows
