from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    price: float = Field(gt=0)


class Item(ItemCreate):
    id: int


class Message(BaseModel):
    name: str
    message: str
