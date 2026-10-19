from fastapi import APIRouter, HTTPException, status

from app.schemas import Item, ItemCreate

router = APIRouter(prefix="/items", tags=["items"])

# In-memory store for the dummy endpoints; replace with a real database later.
_items: dict[int, Item] = {}
_next_id = 1


@router.get("", response_model=list[Item])
def list_items() -> list[Item]:
    return list(_items.values())


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    item = _items.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    global _next_id
    item = Item(id=_next_id, **payload.model_dump())
    _items[item.id] = item
    _next_id += 1
    return item
