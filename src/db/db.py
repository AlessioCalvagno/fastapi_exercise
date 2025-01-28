import sqlite3
from sqlite3 import Connection, Cursor
from typing import Generator, Any

from loguru import logger


async def get_connection() -> Generator[Connection, Any, None]:
    """
    Function to be used to inject db connection via dependency injection
    """
    with sqlite3.connect("items.db", autocommit=True) as connection:
        yield connection


async def _init_records(cursor: Connection):
    logger.debug("Database is empty.")
    logger.debug("Inserting records into db table")
    data: tuple[dict[str, Any], ...] = (
        {
            "ID": 1,
            "NAME": "item1",
            "QUANTITY": 2
        },
        {
            "ID": 2,
            "NAME": "item2",
            "QUANTITY": 0
        },
        {
            "ID": 3,
            "NAME": "item3",
            "QUANTITY": 4
        }
    )

    cursor.executemany("INSERT INTO ITEMS (ID, NAME, QUANTITY) VALUES (:ID, :NAME, :QUANTITY)",
                               data)

async def create_db_and_table():
    with sqlite3.connect("items.db", autocommit=True) as tmp_connection:
        logger.info("Database start up...")
        logger.debug("Check if table already exists")

        tmp_connection.execute("""CREATE TABLE IF NOT EXISTS ITEMS (
                    ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    NAME VARCHAR(255) NOT NULL,
                    QUANTITY INT NOT NULL DEFAULT 0
                    );
                    """)

        res: Cursor = tmp_connection.execute("""SELECT COUNT(*) AS TOTAL FROM ITEMS
                    """)
        is_table_empty: bool = res.fetchone()[0] == 0
        
        if is_table_empty:
            _init_records(cursor=tmp_connection)
        
        logger.info("Database init complete")
        
 