from fastapi import APIRouter, HTTPException, Depends
from app.functions.item import add_item_to_cart, update_item_note, delete_item, retrieve_cart_items, add_new_item_across_carts, modify_existing_item_across_carts, nuke
from app.functions.base import Item, EditNoteRequest, AddNewItemRequest
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.utils.rate_limiter import rate_limit

router = APIRouter()

@router.post("/{cart_id}/items")
async def add_item(
    cart_id: str,
    payload: Item,
    current_user: User = Depends(get_current_user)
):
    """Add an item to a specific cart."""
    try:
        item_as_dict = payload.model_dump()
        if item_as_dict.get("image"):
            item_as_dict["image"] = str(item_as_dict["image"])
        if item_as_dict.get("url"):
            item_as_dict["url"] = str(item_as_dict["url"])

        # Pass the converted dictionary to the model function
        response = await add_item_to_cart(current_user.email, cart_id, item_as_dict)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#GET ITEMS
@router.get("/{cart_id}/items")
async def get_cart_items(
    cart_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all items from a specific cart.
    """
    try:
        response = await retrieve_cart_items(current_user.email, cart_id)
        return response
    except ValueError as e:
        # Handle not found cases with 404
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# EDIT ITEMS NOTES
@router.put("/items/{item_id}/edit-note")
async def edit_item_note(
    item_id: str,
    payload: EditNoteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Edit the note for all occurrences of the item across all carts.
    """
    try:
        response = await update_item_note(current_user.email, item_id, payload.new_note)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE ITEM
@router.delete("/{cart_id}/items/{item_id}")
async def remove_item(
    cart_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific item from a cart and update its selected_cart_ids.
    If the item is in other carts, remove the cart_id from selected_cart_ids.
    If the item is only in one cart, fully delete it.
    """
    try:
        response = await delete_item(current_user.email, cart_id, item_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ROUTE: Add new item across selected carts
@router.post("/items/add-new")
async def add_new_item(
    payload: AddNewItemRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Add a new item across selected carts with a unique item_id.
    """
    try:
        # Convert Pydantic object to a plain dictionary with URLs converted to strings
        item_details = payload.model_dump()
        if item_details.get("image"):
            item_details["image"] = str(item_details["image"])
        if item_details.get("url"):
            item_details["url"] = str(item_details["url"])

        response = await add_new_item_across_carts(current_user.email, item_details, payload.selected_cart_ids)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ROUTE: Modify existing item across selected carts
@router.put("/items/{item_id}/move")
async def move_item(
    item_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Move an existing item across selected carts.
    """
    try:
        selected_cart_ids = payload.get("selected_cart_ids", [])
        response = await modify_existing_item_across_carts(current_user.email, item_id, selected_cart_ids)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#DELETE ALL ITEM INSTANCES
@router.delete("/items/{item_id}/nuke")
async def remove_item_from_all(
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an item from all carts for a user."""
    try:
        response = await nuke(current_user.email, item_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
