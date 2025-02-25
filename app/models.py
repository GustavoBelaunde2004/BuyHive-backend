from datetime import datetime
from uuid import uuid4  # For generating unique IDs
from .database import cart_collection

import yagmail

# Your Gmail credentials
GMAIL_USER = "gabelaunde@gmail.com"
GMAIL_PASSWORD = "hqtq alsv aqch uoad"

yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASSWORD)

def send_email_gmail(recipient_email, cart_name, cart_items):
    """Send a professional email with optimized spacing (no extra <br> tags)."""
    subject = f"Your Shared Cart: {cart_name}"

    # BuyHive banner with explicit padding and dark mode fix
    banner_color_light = "hsl(42, 95%, 66%)"  # Default color
    banner_color_dark = "hsl(42, 100%, 75%)"  # Brighter for dark mode

    header_html = f"""
    <div class="banner" style="background-color: {banner_color_light}; padding: 12px 20px; text-align: center; margin: 0;">
        <h1 style="color: white; font-size: 24px; margin: 0; padding: 0; line-height: 1.2; display: block;">BuyHive</h1>
    </div>
    """

    # Force the correct color in dark mode
    header_html += f"""
    <div style="display:none; color-scheme:dark; background-color: {banner_color_dark} !important;">
        <h1 style="color: white !important; margin: 0; padding: 0; line-height: 1.2; display: block;">BuyHive 🛒</h1>
    </div>
    """

    # Cart name section
    cart_html = f"""
    <div style="padding: 5px 5px; text-align: center; margin: 0;">
        <h2 style="color: #333; font-size: 20px; margin: 0; padding: 0; line-height: 1.2; display: block;">Your Shared Cart: <strong>{cart_name}</strong></h2>
        <p style="color: #666; font-size: 14px; margin: 0; padding: 0; line-height: 1.2; display: block;">Here are the items you’ve added:</p>
    </div>
    """

    # Product listing with notes added
    items_html = "".join([
        f"""
        <div style="display: flex; align-items: center; padding: 10px 15px; border-bottom: 1px solid #ddd; margin: 0;">
            <img src="{item['image']}" alt="{item['name']}" style="width: 70px; height: 70px; border-radius: 8px; margin-right: 12px;">
            <div>
                <h3 style="margin: 0; padding: 0; color: #333; font-size: 16px; line-height: 1.2; display: block;">{item['name']}</h3>
                <p style="margin: 3px 0 0 0; padding: 0; font-size: 14px; color: #666; line-height: 1.2; display: block;">${item['price']}</p>
                {"<p style='font-size: 13px; color: #888; font-style: italic; margin: 3px 0 0 0; padding: 0; line-height: 1.2; display: block;'>Note: " + item['notes'] + "</p>" if 'notes' in item and item['notes'] else ""}
            </div>
        </div>
        """ for item in cart_items
    ])

    # Footer with better spacing
    footer_html = """
    <div style="padding: 5px; text-align: center; color: #999; font-size: 12px; margin: 0;">
        <p style="margin: 0; padding: 0; line-height: 1.2; display: block;">Thank you for using BuyHive! 🐝</p>
        <p style="font-size: 10px; margin: 5px 0 0 0; padding: 0; line-height: 1.2; display: block;">Need help? <a href="#" style="color: #555; text-decoration: none;">Contact Support</a></p>
    </div>
    """

    # Combine all sections
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f9f9f9;">
        {header_html}
        <div style="background-color: white; max-width: 600px; margin: 5px auto; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); overflow: hidden;">
            {cart_html}
            <div style="padding: 5px; margin: 0;">{items_html}</div>
        </div>
        {footer_html}
    </body>
    </html>
    """

    try:
        yag.send(to=recipient_email, subject=subject, contents=body_html)
        return {"message": "Email sent successfully!"}
    except Exception as e:
        return {"error": str(e)}


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

#DELETE
async def delete_item(email: str, cart_id: str, item_id: str):
    """
    Delete a specific item from a cart and update its selected_cart_ids.
    If the item is in other carts, remove the cart from selected_cart_ids.
    If it’s the last cart, fully remove the item.
    """
    # Step 1: Remove the item from the specific cart
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {
            "$pull": {"carts.$.items": {"item_id": item_id}},
            "$inc": {"carts.$.item_count": -1}
        }
    )

    # Step 2: Check if the item exists in any other carts
    user_data = await cart_collection.find_one(
        {"email": email, "carts.items.item_id": item_id},
        {"carts.items.$": 1}
    )

    if user_data:
        # Item still exists in other carts, update `selected_cart_ids`
        await cart_collection.update_many(
            {"email": email, "carts.items.item_id": item_id},
            {"$pull": {"carts.$[].items.$[item].selected_cart_ids": cart_id}},
            array_filters=[{"item.item_id": item_id}]
        )
        return {"message": f"Item removed from cart {cart_id}, updated selected_cart_ids."}
    
    return {"message": "Item fully deleted from all carts."} if result.modified_count else {"message": "Cart or item not found!"}



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
async def modify_existing_item_across_carts(email: str, item_id: str, selected_cart_ids: list):
    """
    Move an existing item between selected carts.
    - Ensures the item is **added** to selected carts **if not already there**.
    - Ensures the item is **removed** from deselected carts.
    - Updates the `selected_cart_ids` attribute correctly.
    """

    # Step 1: Retrieve the item details from ANY cart
    user_data = await cart_collection.find_one(
        {"email": email, "carts.items.item_id": item_id},
        {"carts.items.$": 1}  # Retrieve the first cart that contains this item
    )

    if not user_data or "carts" not in user_data or not user_data["carts"]:
        return {"message": "Item not found!"}

    # Extract the item details
    item = next(
        (i for c in user_data["carts"] for i in c["items"] if i["item_id"] == item_id),
        None
    )

    if not item:
        return {"message": "Item not found!"}

    # Step 2: Get all the carts the item is currently in
    existing_carts = await cart_collection.find(
        {"email": email, "carts.items.item_id": item_id},
        {"carts.cart_id": 1}
    ).to_list(length=None)

    current_cart_ids = [c["carts"][0]["cart_id"] for c in existing_carts if c.get("carts")]

    # Determine carts to remove from (carts that are not in `selected_cart_ids`)
    remove_from_cart_ids = list(set(current_cart_ids) - set(selected_cart_ids))

    # Step 3: Remove the item from carts that are no longer selected
    if remove_from_cart_ids:
        await cart_collection.update_many(
            {
                "email": email,
                "carts.cart_id": {"$in": remove_from_cart_ids},
                "carts.items.item_id": item_id
            },
            {
                "$pull": {"carts.$.items": {"item_id": item_id}},
                "$inc": {"carts.$.item_count": -1}
            }
        )

    # Step 4: Add the item to selected carts (if not already there)
    for cart_id in selected_cart_ids:
        cart_data = await cart_collection.find_one(
            {"email": email, "carts.cart_id": cart_id, "carts.items.item_id": item_id}
        )

        if not cart_data:  # If item is NOT in this cart, add it
            item_copy = item.copy()
            item_copy.pop("added_at", None)  # Ensure the original timestamp is not modified

            await cart_collection.update_one(
                {"email": email, "carts.cart_id": cart_id},
                {
                    "$push": {"carts.$.items": item_copy},
                    "$inc": {"carts.$.item_count": 1}
                }
            )

    # Step 5: Update `selected_cart_ids` for all occurrences of the item
    updated_cart_ids = list(set(selected_cart_ids))  # Remove duplicates
    await cart_collection.update_many(
        {"email": email, "carts.items.item_id": item_id},
        {
            "$set": {"carts.$[].items.$[item].selected_cart_ids": updated_cart_ids}
        },
        array_filters=[{"item.item_id": item_id}]
    )

    return {"message": "Item successfully moved across selected carts."}
