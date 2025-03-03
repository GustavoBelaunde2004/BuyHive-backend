from fastapi import APIRouter, HTTPException
from app.functions.item import add_item_to_cart,update_item_note,delete_item,retrieve_cart_items,add_new_item_across_carts,modify_existing_item_across_carts
from app.functions.base import Item,EditNoteRequest,AddNewItemRequest

router = APIRouter()

@router.post("/carts/{email}/{cart_id}/items")
async def add_item(email: str, cart_id: str, payload: Item):
    """Add an item to a specific cart."""
    try:
        item_as_dict = payload.model_dump()
        if item_as_dict.get("image"):
            item_as_dict["image"] = str(item_as_dict["image"])
        if item_as_dict.get("url"):
            item_as_dict["url"] = str(item_as_dict["url"])

        # Pass the converted dictionary to the model function
        response = await add_item_to_cart(email, cart_id, item_as_dict)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#GET ITEMS
@router.get("/carts/{email}/{cart_id}/items")
async def get_cart_items(email: str, cart_id: str):
    """
    Retrieve all items from a specific cart.
    """
    try:
        response = await retrieve_cart_items(email, cart_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# EDIT ITEMS NOTES
@router.put("/carts/{email}/items/{item_id}/edit-note")
async def edit_item_note(email: str, item_id: str, payload: EditNoteRequest):
    """
    Edit the note for all occurrences of the item across all carts.
    """
    try:
        response = await update_item_note(email, item_id, payload.new_note)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE ITEM
@router.delete("/carts/{email}/{cart_id}/items/{item_id}")
async def remove_item(email: str, cart_id: str, item_id: str):
    """
    Delete a specific item from a cart and update its selected_cart_ids.
    If the item is in other carts, remove the cart_id from selected_cart_ids.
    If the item is only in one cart, fully delete it.
    """
    try:
        response = await delete_item(email, cart_id, item_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ROUTE: Add new item across selected carts
@router.post("/carts/{email}/items/add-new")
async def add_new_item(email: str, payload: AddNewItemRequest):
    """
    Add a new item across selected carts with a unique item_id.
    """
    try:
        # Convert Pydantic object to a plain dictionary with URLs converted to strings
        item_details = payload.dict()
        if item_details.get("image"):
            item_details["image"] = str(item_details["image"])
        if item_details.get("url"):
            item_details["url"] = str(item_details["url"])

        response = await add_new_item_across_carts(email, item_details, payload.selected_cart_ids)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ROUTE: Modify existing item across selected carts
@router.put("/carts/{email}/items/{item_id}/move")
async def move_item(email: str, item_id: str, payload: dict):
    """
    Move an existing item across selected carts.
    """
    try:
        selected_cart_ids = payload.get("selected_cart_ids", [])
        response = await modify_existing_item_across_carts(email, item_id, selected_cart_ids)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
