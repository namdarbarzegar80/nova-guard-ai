import aiosqlite

DB_PATH = "nova_guard.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                anti_link INTEGER DEFAULT 0,
                anti_flood INTEGER DEFAULT 0,
                welcome INTEGER DEFAULT 0,
                warn_limit INTEGER DEFAULT 3
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                chat_id INTEGER,
                user_id INTEGER,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS filtered_words (
                chat_id INTEGER,
                word TEXT,
                UNIQUE(chat_id, word)
            )
        """)

        await db.commit()


async def ensure_group(chat_id):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO groups (chat_id)
            VALUES (?)
            """,
            (chat_id,)
        )

        await db.commit()


async def get_settings(chat_id):

    await ensure_group(chat_id)

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT
                chat_id,
                anti_link,
                anti_flood,
                welcome,
                warn_limit
            FROM groups
            WHERE chat_id = ?
            """,
            (chat_id,)
        )

        return await cursor.fetchone()


async def set_setting(chat_id, setting, value):

    allowed = {
        "anti_link",
        "anti_flood",
        "welcome",
        "warn_limit"
    }

    if setting not in allowed:
        return

    await ensure_group(chat_id)

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            f"""
            UPDATE groups
            SET {setting} = ?
            WHERE chat_id = ?
            """,
            (value, chat_id)
        )

        await db.commit()


async def add_warning(chat_id, user_id):

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO warnings
            (chat_id, user_id, count)
            VALUES (?, ?, 0)
            """,
            (chat_id, user_id)
        )

        await db.execute(
            """
            UPDATE warnings
            SET count = count + 1
            WHERE chat_id = ? AND user_id = ?
            """,
            (chat_id, user_id)
        )

        cursor = await db.execute(
            """
            SELECT count
            FROM warnings
            WHERE chat_id = ? AND user_id = ?
            """,
            (chat_id, user_id)
        )

        row = await cursor.fetchone()

        await db.commit()

        return row[0]


async def add_word(chat_id, word):

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO filtered_words
            (chat_id, word)
            VALUES (?, ?)
            """,
            (chat_id, word.lower())
        )

        await db.commit()


async def remove_word(chat_id, word):

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            DELETE FROM filtered_words
            WHERE chat_id = ? AND word = ?
            """,
            (chat_id, word.lower())
        )

        await db.commit()


async def get_words(chat_id):

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            SELECT word
            FROM filtered_words
            WHERE chat_id = ?
            ORDER BY word
            """,
            (chat_id,)
        )

        rows = await cursor.fetchall()

        return [row[0] for row in rows]
