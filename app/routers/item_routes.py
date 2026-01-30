from fastapi import APIRouter, HTTPException, Depends
from app.schemas.item import EditNoteRequest, AddNewItemRequest, MoveItemRequest
from app.services.item_service import ItemService, DuplicateItemError
from app.core.dependencies import get_current_user, get_item_service
from app.models.user import User
from app.utils.rate_limiter import rate_limit

router = APIRouter()

@router.get("/{cart_id}/items", response_model=dict)
async def get_cart_items(
    cart_id: str,
    current_user: User = Depends(get_current_user),
    item_service: ItemService = Depends(get_item_service)
):
    """
    Retrieve all items from a specific cart.
    """
    try:
        items = await item_service.get_cart_items(current_user.user_id, cart_id)
        return {"items": items}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/items/{item_id}/edit-note", response_model=dict)
async def edit_item_note(
    item_id: str,
    payload: EditNoteRequest,
    current_user: User = Depends(get_current_user),
    item_service: ItemService = Depends(get_item_service)
):
    """
    Edit the note for all occurrences of the item across all carts.
    """
    try:
        updated_item = await item_service.update_item_note(
            current_user.user_id, 
            item_id, 
            payload.new_note
        )
        return {"message": "Item note updated successfully", "item": updated_item}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{cart_id}/items/{item_id}", response_model=dict)
async def remove_item(
    cart_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    item_service: ItemService = Depends(get_item_service)
):
    """
    Delete a specific item from a cart and update its selected_cart_ids.
    If the item is in other carts, remove the cart_id from selected_cart_ids.
    If the item is only in one cart, fully delete it.
    """
    try:
        response = await item_service.delete_item(
            current_user.user_id, 
            cart_id, 
            item_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/items/add-new", response_model=dict)
async def add_new_item(
    payload: AddNewItemRequest,
    current_user: User = Depends(get_current_user),
    item_service: ItemService = Depends(get_item_service)
):
    """
    Add a new item across selected carts with a unique item_id.
    """
    try:
        item_details = payload.model_dump()
        if item_details.get("image"):
            item_details["image"] = str(item_details["image"])
        if item_details.get("url"):
            item_details["url"] = str(item_details["url"])

        response = await item_service.create_item(
            current_user.user_id, 
            item_details, 
            payload.selected_cart_ids
        )
        return response
    except DuplicateItemError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "message": str(e),
                "existing_item": e.existing_item
            }
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/items/{item_id}/move", response_model=dict)
async def move_item(
    item_id: str,
    payload: MoveItemRequest,
    current_user: User = Depends(get_current_user),
    item_service: ItemService = Depends(get_item_service)
):
    """
    Move an existing item across selected carts.
    """
    try:
        updated_item = await item_service.move_item(
            current_user.user_id, 
            item_id, 
            payload.selected_cart_ids
        )
        return {"message": "Item moved successfully", "item": updated_item}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/items/{item_id}/nuke", response_model=dict)
async def remove_item_from_all(
    item_id: str,
    current_user: User = Depends(get_current_user),
    item_service: ItemService = Depends(get_item_service)
):
    """Delete an item from all carts for a user."""
    try:
        response = await item_service.delete_item_from_all_carts(
            current_user.user_id, 
            item_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
