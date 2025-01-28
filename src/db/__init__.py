from typing import Annotated, TypeAlias
from sqlite3 import Connection
from fastapi import Depends
from .db import get_connection, create_db_and_table

DbDep: TypeAlias = Annotated[Connection, Depends(get_connection)]