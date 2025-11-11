class UserRepo:
    def __init__(self, db):
        self.db = db

    async def get_or_create(self, tg_id, username, first_name):
        row = await self.db.fetchone(
            "SELECT id FROM users WHERE tg_id = ?",
            (tg_id,)
        )
        if row:
            return row[0]

        cursor = await self.db.execute(
            "INSERT INTO users (tg_id, username, first_name) VALUES (?, ?, ?)",
            (tg_id, username, first_name)
        )
        return cursor.lastrowid
