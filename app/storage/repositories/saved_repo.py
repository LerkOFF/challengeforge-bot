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

    async def save_with_note(self, user_id: int, challenge_id: int, note: str):
        await self.db.execute(
            """
            INSERT INTO saved (user_id, challenge_id, note)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, challenge_id)
            DO UPDATE SET note = excluded.note
            """,
            (user_id, challenge_id, note),
        )

    async def count_for_user(self, user_id: int) -> int:
        row = await self.db.fetchone("SELECT COUNT(*) FROM saved WHERE user_id = ?", (user_id,))
        return int(row[0]) if row and row[0] is not None else 0

    async def page_for_user(self, user_id: int, limit: int, offset: int):
        # cid, title, score
        rows = await self.db.fetchall(
            """
            SELECT c.id, c.title, COALESCE(SUM(v.value), 0) AS score
            FROM saved s
            JOIN challenges c ON c.id = s.challenge_id
            LEFT JOIN votes v ON v.challenge_id = c.id
            WHERE s.user_id = ?
            GROUP BY c.id
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (user_id, limit, offset),
        )
        return rows
