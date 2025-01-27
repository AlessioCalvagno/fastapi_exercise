"""
Scrivi una RESTful API (con FastAPI) che implementi i seguenti endpoint:
• GET /items: Restituisce una lista di elementi.
• POST /items: Aggiunge un nuovo elemento.
• PUT /items/{item_id}: Aggiorna completamente un elemento esistente.
• PATCH /items/{item_id}: Aggiorna parzialmente un elemento esistente.
• DELETE /items/{item_id}: Elimina un elemento
"""

from fastapi import FastAPI, status, HTTPException
from model import Item, ItemDTO
from pydantic import NonNegativeInt
from typing import Any
from exc import NotFoundError
from loguru import logger
# import logging
# from logging import Logger

item1: Item = Item(**{
    "id":1,
    "name":"item1",
    "quantity":2})

item2: Item = Item(**{
    "id":2,
    "name":"item2",
    "quantity":0})

item3: Item = Item(**{
    "id":3,
    "name":"item3",
    "quantity":4})

fake_db: list[Item] = [item1,item2,item3]


#entry point per fastAPI
app = FastAPI()

#logger
# logger: Logger = logging.getLogger(__name__)

# le varie chiamate si definiscono creando una funzione e mettendo un decorator alla funzione
# usando lo stesso oggetto 'app' appena creato. Il percorso dell'endpoint è indicato come
# stringa.

# chiamata GET
@app.get("/items", status_code=status.HTTP_200_OK)
async def get_items() -> list[Item]:
    try:
        return fake_db
    except Exception as e:
        logger.error(f"Exception occured: {e}")
        logger.error(f"Error in retrieving items", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?

# chiamata POST
@app.post("/items", status_code=status.HTTP_200_OK)
async def add_item(item: Item) -> Item: #nota: il fatto che il tipo sia Item e non Item | None, rende il body obbligatorio
    try:
        item.id = _get_last_id() + 1
        fake_db.append(item)
        return item
    except Exception as e:
        logger.error(f"Exception occured: {e}")
        logger.error(f"Error in adding item: {item}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?

# chiamata PUT
@app.put("/items/{item_id}", status_code=status.HTTP_200_OK)
async def full_update_item(item_id: NonNegativeInt, new_item: Item) -> Item:
    try:
        old_item : Item = _get_by_id(item_id)
        fake_db.remove(old_item)

        #keep old id
        new_item.id = item_id
        fake_db.append(new_item)

        return new_item

    except NotFoundError as e:
        logger.error(f"Exception occured: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item_id not found")

    except Exception as e:
        logger.error(f"Exception occured: {e}")
        logger.error(f"Error in updating item: {item_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?


# chiamata patch
@app.patch("/items/{item_id}", status_code=status.HTTP_200_OK)
async def part_update_item(item_id: NonNegativeInt, item_dto: ItemDTO) -> Item:
    try:
        old_item : Item = _get_by_id(item_id)
        old_item_dict: dict[str, Any] = old_item.model_dump()
        new_item_dict: dict[str, Any] = {}
        for name, value in item_dto:

            if value is None or value == old_item_dict[name]:
                new_item_dict[name] = old_item_dict[name]
            else:
                new_item_dict[name] = value
        
        new_item = Item(**new_item_dict)
        new_item.id = old_item.id

        fake_db.remove(old_item)
        fake_db.append(new_item)

        return new_item
    
    except NotFoundError as e:
        logger.error(f"Exception occured: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item_id not found")
    
    except Exception as e:
        logger.error(f"Exception occured: {e}")
        logger.error(f"Error in updating item: {item_id}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?


# chiamata delete
@app.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def delete_by_id(item_id: NonNegativeInt) -> dict[str, str]:
    try:
        fake_db.remove(_get_by_id(item_id))
        return {"detail":f"Item with id {item_id} removed"}
    except NotFoundError as e:
        logger.exception(f"Exception occured: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item_id not found")
    except Exception as e:
        logger.error(f"Exception occured: {e}")
        logger.exception(f"Error in updating item: {item_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) #TODO serve un detail qui?


# TODO questi due metodi andrebbero in un service a parte
def _get_last_id() -> int:
    fake_db.sort(key=lambda i: i.id)
    return fake_db[-1].id

def _get_by_id(item_id: NonNegativeInt) -> Item:
    for item in fake_db:
        if item.id == item_id:
            return item
    raise NotFoundError(item_id)