"""
Uso un file separato per definire il model usato nell'esercizio.
Di solito fatAPI usa pydantic, quindi seve anche come esempio per
familiarizzare con pydantic
"""

from pydantic import BaseModel, NonNegativeInt

class Item(BaseModel):
    id: NonNegativeInt | None = None
    name: str
    quantity: NonNegativeInt

#questo è usato per gli update parziali, per poter gestire i casi quando non tutti i campi sono passati
#e quindi tutti i campi hanno il default None
class ItemDTO(BaseModel):
    id: NonNegativeInt | None = None
    name: str | None = None
    quantity: NonNegativeInt | None = None