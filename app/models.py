from datetime import datetime
from uuid import uuid4  # For generating unique IDs
from .database import cart_collection
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Initialize SES client
ses_client = boto3.client('ses', region_name='us')

# EMAIL FUNCTIONS --------------------------------------------------------------------------------------------------------------
async def send_cart_email(sender_email: str, recipient_email: str, cart_name: str, cart_items: list):
    subject = f"Shared Cart: {cart_name}"
    
    # Format cart items into a readable list
    item_list = "\n".join([f"- {item['name']} (${item['price']})" for item in cart_items])
    
    body_text = f"""
    You've received a shart cart named '{cart_name}'.

    Items:
    {item_list}

    Happy Shopping!
    """

    try:
        # Send the email
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Text': {
                        'Data': body_text
                    }
                }
            }
        )
        return {"message": "Email sent successfully!", "MessageId": response['MessageId']}
    except (NoCredentialsError, PartialCredentialsError) as e:
        return {"error": f"AWS credentials issue: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}

# USER FUNCTIONS --------------------------------------------------------------------------------------------------------------
async def add_user_by_email(email: str, name: str = "Unknown"):
    """Add a new user to the database or ensure they already exist."""
    existing_user = await cart_collection.find_one({"email": email})
    if existing_user:
        return {"message": "User already exists!"}

    new_user = {
        "email": email,
        "name": name,
        "cart_count": 0,
        "carts": []
    }
    await cart_collection.insert_one(new_user)
    return {"message": "User added successfully!"}

# CART FUNCTIONS --------------------------------------------------------------------------------------------------------------
# POST
async def save_cart(email: str, cart_name: str):
    """Add a new cart with a unique ID for a user and update the cart count."""
    existing_cart = await cart_collection.find_one({"email": email, "carts.cart_name": cart_name})
    if existing_cart:
        return {"message": "Cart already exists!"}

    cart_id = str(uuid4())  # Generate unique cart_id
    result = await cart_collection.update_one(
        {"email": email},
        {
            "$push": {
                "carts": {
                    "cart_id": cart_id,
                    "cart_name": cart_name,
                    "item_count": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "items": []
                }
            },
            "$inc": {"cart_count": 1}
        },
        upsert=True
    )

    if result.upserted_id:
        return {"message": "Cart created successfully!", "cart_id": cart_id}
    elif result.modified_count > 0:
        return {"message": "Cart added successfully!", "cart_id": cart_id}
    else:
        return {"message": "No changes made."}

# PUT
async def update_cart_name(email: str, cart_id: str, new_name: str):
    """Update the name of a specific cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {"$set": {"carts.$.cart_name": new_name}}
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart name updated successfully!"}

# GET
async def get_carts(email: str):
    """Retrieve all carts for a user."""
    user_data = await cart_collection.find_one({"email": email})
    return user_data.get("carts", []) if user_data else []

# DELETE
async def delete_cart(email: str, cart_id: str):
    """Delete a specific cart and update the cart count."""
    result = await cart_collection.update_one(
        {"email": email},
        {
            "$pull": {"carts": {"cart_id": cart_id}},
            "$inc": {"cart_count": -1}
        }
    )
    if result.modified_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart deleted successfully!"}

# ITEM FUNCTIONS --------------------------------------------------------------------------------------------------------------
# POST
async def add_item_to_cart(email: str, cart_id: str, item: dict):
    """Add an item with a unique ID to a specific cart and update the item count."""
    item["item_id"] = str(uuid4())  # Generate unique item_id
    item["added_at"] = datetime.utcnow().isoformat()

    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {
            "$push": {"carts.$.items": item},
            "$inc": {"carts.$.item_count": 1}
        }
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Item added successfully!", "item_id": item["item_id"]}

#GET items from cart
async def retrieve_cart_items(email: str, cart_id: str):
    """
    Retrieve all items from a specific cart for a given user.
    """
    user_data = await cart_collection.find_one(
        {"email": email, "carts.cart_id": cart_id},
        {"carts.$": 1}  # Project only the matching cart
    )

    if not user_data or "carts" not in user_data or not user_data["carts"]:
        return {"message": "Cart not found!"}

    # Extract the cart items
    cart = user_data["carts"][0]
    return {"cart_id": cart["cart_id"], "cart_name": cart["cart_name"], "items": cart["items"]}



# PUT (EDIT ALL ITEMS)
async def update_cart_items(email: str, cart_id: str, items: list):
    """Update all items in a specific cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {"$set": {"carts.$.items": items}}
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart items updated successfully!"}

# PUT (Edits notes for all apereances of saem item in every car per user)
async def update_item_note(email: str, item_id: str, new_note: str):
    """
    Update the note for all occurrences of the item across all carts of a user.
    """
    result = await cart_collection.update_many(
        {
            "email": email,
            "carts.items.item_id": item_id  # Find any cart containing the item
        },
        {
            "$set": {"carts.$[cart].items.$[item].notes": new_note}  # Update only matching items
        },
        array_filters=[
            {"cart.items.item_id": item_id},  # Matches carts containing the item
            {"item.item_id": item_id}  # Matches specific item within the cart
        ]
    )

    if result.modified_count == 0:
        return {"message": "No items were updated. Item not found or no changes made."}

    return {"message": f"Successfully updated {result.modified_count} item(s) across carts."}



# DELETE
async def delete_item(email: str, cart_id: str, item_id: str):
    """Delete a specific item from a cart and update the item count."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {
            "$pull": {"carts.$.items": {"item_id": item_id}},
            "$inc": {"carts.$.item_count": -1}
        }
    )
    if result.modified_count == 0:
        return {"message": "Cart or item not found!"}
    return {"message": "Item deleted successfully!"}


#TEST---------------------------------------------------------------------------------------------------------------------------------------------

# ADD NEW ITEM ACROSS SELECTED CARTS
async def add_new_item_across_carts(email: str, item_details: dict, selected_cart_ids: list):
    """
    Add a new item with a unique item_id across selected carts.
    """
    item_details["item_id"] = str(uuid4())  # Generate unique item_id
    item_details["added_at"] = datetime.utcnow().isoformat()

    # Step 1: Add the item to each selected cart
    for cart_id in selected_cart_ids:
        item_copy = item_details.copy()
        await cart_collection.update_one(
            {"email": email, "carts.cart_id": cart_id},
            {
                "$push": {"carts.$.items": item_copy},
                "$inc": {"carts.$.item_count": 1}
            }
        )

    return {"message": "New item added successfully across selected carts."}

# MODIFY EXISTING ITEM ACROSS CARTS
async def modify_existing_item_across_carts(email: str, item_id: str, add_to_cart_ids: list, remove_from_cart_ids: list):
    """
    Modify an existing item's presence across selected/deselected carts.
    """
    # Step 1: Find the item details from any cart
    user_data = await cart_collection.find_one(
        {"email": email, "carts.items.item_id": item_id},
        {"carts.$": 1}
    )

    if not user_data or "carts" not in user_data or not user_data["carts"]:
        return {"message": "Item not found!"}

    # Retrieve item details
    item = next(
        (i for i in user_data["carts"][0]["items"] if i["item_id"] == item_id),
        None
    )

    if not item:
        return {"message": "Item not found!"}

    # Step 2: Remove the item from deselected carts
    if remove_from_cart_ids:
        await cart_collection.update_many(
            {"email": email, "carts.cart_id": {"$in": remove_from_cart_ids}},
            {
                "$pull": {"carts.$.items": {"item_id": item_id}},
                "$inc": {"carts.$.item_count": -1}
            }
        )

    # Step 3: Add the item to newly selected carts
    if add_to_cart_ids:
        for cart_id in add_to_cart_ids:
            item_copy = item.copy()
            item_copy["added_at"] = datetime.utcnow().isoformat()  # Update timestamp
            await cart_collection.update_one(
                {"email": email, "carts.cart_id": cart_id},
                {
                    "$push": {"carts.$.items": item_copy},
                    "$inc": {"carts.$.item_count": 1}
                }
            )

    return {"message": "Item successfully modified across selected carts."}

