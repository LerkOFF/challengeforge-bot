class ChallengeRepo:
    def __init__(self, db):
        self.db = db

    async def create(self, title: str, body: str, tags: str):
        cursor = await self.db.execute(
            "INSERT INTO challenges (title, body, tags) VALUES (?, ?, ?)",
            (title, body, tags)
        )
        return cursor.lastrowid

    async def get_random(self):
        row = await self.db.fetchone(
            "SELECT id, title, body, tags FROM challenges ORDER BY RANDOM() LIMIT 1"
        )
        return row
