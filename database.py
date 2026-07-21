import sqlite3

from config import DATABASE


class Database:

    def __init__(self):

        self.conn = sqlite3.connect(
            DATABASE,
            check_same_thread=False
        )

        self.cur = self.conn.cursor()

        self.create_tables()

    def create_tables(self):

        self.cur.execute("""

        CREATE TABLE IF NOT EXISTS users(

            telegram_id INTEGER PRIMARY KEY,

            username TEXT,

            first_name TEXT

        )

        """)

        self.cur.execute("""

        CREATE TABLE IF NOT EXISTS services(

            telegram_id INTEGER,

            email TEXT,

            uuid TEXT,

            inbound INTEGER,

            volume INTEGER,

            days INTEGER,

            subscription TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

        self.conn.commit()

    def add_user(
        self,
        telegram_id,
        username,
        first_name
    ):

        self.cur.execute("""

        INSERT OR IGNORE INTO users
        VALUES(?,?,?)

        """, (

            telegram_id,
            username,
            first_name

        ))

        self.conn.commit()

    def save_service(

        self,

        telegram_id,

        email,

        uuid,

        inbound,

        volume,

        days,

        subscription

    ):

        self.cur.execute("""

        INSERT INTO services
        VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)

        """, (

            telegram_id,
            email,
            uuid,
            inbound,
            volume,
            days,
            subscription

        ))

        self.conn.commit()

    def get_service(
        self,
        telegram_id
    ):

        self.cur.execute("""

        SELECT *

        FROM services

        WHERE telegram_id=?

        ORDER BY created_at DESC

        LIMIT 1

        """, (

            telegram_id,

        ))

        return self.cur.fetchone()
