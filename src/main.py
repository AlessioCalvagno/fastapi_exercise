"""
Scrivi una RESTful API (con FastAPI) che implementi i seguenti endpoint:
• GET /items: Restituisce una lista di elementi.
• POST /items: Aggiunge un nuovo elemento.
• PUT /items/{item_id}: Aggiorna completamente un elemento esistente.
• PATCH /items/{item_id}: Aggiorna parzialmente un elemento esistente.
• DELETE /items/{item_id}: Elimina un elemento


Qui uso sqlite
"""

from fastapi import FastAPI, status, Depends, Request
from fastapi.responses import JSONResponse
from model import Item, ItemDTO
from pydantic import NonNegativeInt
from typing import Any, Annotated
from exc import NotFoundError
from loguru import logger
from contextlib import asynccontextmanager
from db import create_db_and_table, get_connection
from sqlite3 import Connection, Cursor
import logging
# from logging import Logger

@asynccontextmanager
async def lifespan(_: FastAPI):
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.disabled = True
    logger.info("Application startup...")
    await create_db_and_table()
    yield
    logger.info("Application shutdown...")



#entry point per fastAPI
app = FastAPI(lifespan=lifespan)

#logger
# logger: Logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"An exception occured during [{request.method}] {request.url}")

    return JSONResponse(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           content={"detail":"Something went wrong"},
           media_type='application/problem+json'           
    )


# le varie chiamate si definiscono creando una funzione e mettendo un decorator alla funzione
# usando lo stesso oggetto 'app' appena creato. Il percorso dell'endpoint è indicato come
# stringa.

# chiamata GET
@app.get("/items", status_code=status.HTTP_200_OK)
async def get_items(connection: Annotated[Connection, Depends(get_connection)]) -> list[Item]:
    # try:
       logger.debug("Executing: SELECT * FROM ITEMS")

       records: list[tuple[Any]] = connection.execute("SELECT * FROM ITEMS").fetchall()
       items: list[Item] = [Item(id=id, name=name, quantity=quantity) for id,name,quantity in records]

       return items
    # except Exception as e:
    #     logger.exception(f"Error in retrieving items")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?

# chiamata POST
@app.post("/items", status_code=status.HTTP_200_OK)
async def add_item(item: Item, connection: Annotated[Connection, Depends(get_connection)]) -> Item: #nota: il fatto che il tipo sia Item e non Item | None, rende il body obbligatorio
        item_dict: dict[str, Any] = item.model_dump()


        logger.debug("Executing: INSERT INTO ITEMS (NAME, QUANTITY) VALUES ({name}, {quantity})".format(**item_dict))
        cur: Cursor = connection.execute("INSERT INTO ITEM (NAME, QUANTITY) VALUES (:name, :quantity)",
                            item_dict)
        
        last_id: int | None = cur.lastrowid
        item.id = last_id
        
        return item
    
    # except Exception as e:
    #     logger.exception(f"Error in adding item: {item}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?

# chiamata PUT
@app.put("/items/{item_id}", status_code=status.HTTP_200_OK)
async def full_update_item(item_id: NonNegativeInt, new_item: Item, 
                           connection: Annotated[Connection, Depends(get_connection)]) -> Item:
    # try:
        new_item.id = item_id
        new_item_dict: dict[str, Any] = new_item.model_dump()

        logger.debug("Executing: UPDATE ITEMS SET NAME = {name}, QUANTITY = {quantity} WHERE ID = {id}".format(**new_item_dict))
        connection.execute("UPDATE ITEMS SET NAME = :name, QUANTITY = :quantity WHERE ID = :id",
                           new_item_dict)

        return new_item

    # except Exception as e:
    #     logger.exception(f"Error in updating item: {item_id}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?


# chiamata patch
@app.patch("/items/{item_id}", status_code=status.HTTP_200_OK)
async def part_update_item(item_id: NonNegativeInt, item_dto: ItemDTO,
                           connection: Annotated[Connection, Depends(get_connection)]) -> dict[str, str]:
    # try:
        # TODO togliere i log trace di qui sotto
        item_dto.id = None
        logger.trace(item_dto)
        fields: str = ", ".join([name.upper() + " = " + "{" + name + "}" for name, value in item_dto if value is not None])
        logger.trace(fields)

        query_format:str = "UPDATE ITEMS SET " + fields + " WHERE ID = {id}"
        logger.trace(query_format)

        query: str = query_format.replace("{",":").replace("}","") #TODO: regex??
        logger.trace(query)

        item_dto.id =  item_id
        item_dto_dict: dict[str, Any] = item_dto.model_dump()

        logger.debug(("Executing: " + query_format).format(**item_dto_dict))
        connection.execute(query, item_dto_dict)

        # TODO come torno l'oggetto appena modificato a db con sqlite?
        return {"detail":"OK"} 
    
    # except Exception as e:
    #     logger.error(f"Exception occured: {e}")
    #     logger.error(f"Error in updating item: {item_id}", exc_info=True)
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?


# chiamata delete
@app.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def delete_by_id(item_id: NonNegativeInt, connection: Annotated[Connection, Depends(get_connection)]) -> dict[str, str]:
    # try:
        logger.debug("Executing: DELETE FROM ITEMS WHERE ID = {}".format(item_id))
        connection.execute("DELETE FROM ITEMS WHERE ID = ?", (item_id,))

        return {"detail":f"Item with id {item_id} removed"}
    
    # except Exception as e:
    #     logger.error(f"Exception occured: {e}")
    #     logger.exception(f"Error in updating item: {item_id}")
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?