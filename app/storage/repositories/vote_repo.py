class VoteRepo:
    def __init__(self, db):
        self.db = db

    async def upsert_vote(self, user_id: int, challenge_id: int, value: int):
        await self.db.execute(
            """
            INSERT INTO votes (user_id, challenge_id, value)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, challenge_id) DO UPDATE SET value=excluded.value
            """,
            (user_id, challenge_id, value),
        )

    async def delete_vote(self, user_id: int, challenge_id: int):
        await self.db.execute(
            "DELETE FROM votes WHERE user_id = ? AND challenge_id = ?",
            (user_id, challenge_id),
        )

    async def get_user_vote(self, user_id: int, challenge_id: int) -> int | None:
        row = await self.db.fetchone(
            "SELECT value FROM votes WHERE user_id = ? AND challenge_id = ?",
            (user_id, challenge_id),
        )
        return None if row is None else int(row[0])

    async def get_score(self, challenge_id: int) -> int:
        row = await self.db.fetchone(
            "SELECT COALESCE(SUM(value), 0) FROM votes WHERE challenge_id = ?",
            (challenge_id,),
        )
        return int(row[0] if row and row[0] is not None else 0)
