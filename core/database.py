"""
Async Database Service - Egg Economy Persistence

Uses aiosqlite for non-blocking database operations.

FIXES APPLIED (AI Review):
- Added close() method for lifecycle management (ChatGPT)
"""

import aiosqlite
import os

DB_PATH = os.path.join("data", "math_omni.db")


class DatabaseService:
    """Async database for the egg economy and progress tracking."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._connection = None
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def initialize(self):
        """Create tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS economy (
                    id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    level_id INTEGER PRIMARY KEY,
                    stars INTEGER DEFAULT 0,
                    completed BOOLEAN DEFAULT 0
                )
            """)
            # Init wallet if empty
            async with db.execute("SELECT count(*) FROM economy") as cursor:
                count = await cursor.fetchone()
                if count[0] == 0:
                    await db.execute("INSERT INTO economy (id, balance) VALUES (1, 0)")
            await db.commit()

    async def get_eggs(self) -> int:
        """Get current egg balance."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT balance FROM economy WHERE id=1") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def add_eggs(self, amount: int) -> int:
        """Add eggs and return new total."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE economy SET balance = balance + ? WHERE id=1", (amount,))
            await db.commit()
        return await self.get_eggs()

    async def unlock_level(self, level_id: int):
        """Mark a level as completed."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO progress (level_id, completed) 
                VALUES (?, 1)
            """, (level_id,))
            await db.commit()
    
    async def get_unlocked_level(self) -> int:
        """Returns the maximum unlocked level ID + 1 (next available)."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT MAX(level_id) FROM progress WHERE completed=1") as cursor:
                row = await cursor.fetchone()
                # If level N is done, unlock N+1
                return (row[0] + 1) if row and row[0] else 1
    
    async def close(self) -> None:
        """
        Close database connection.
        FIX: ChatGPT - Lifecycle management for proper shutdown.
        Note: aiosqlite connections are per-query, so this is a no-op,
        but included for interface consistency.
        """
        # aiosqlite uses context managers, so no persistent connection to close
        pass
