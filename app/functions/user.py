from typing import List
from app.config.settings import settings
from .database import cart_collection
from app.models.item import ItemInDB
from app.services.email_service import send_email_ses

async def send_email_gmail(recipient_email: str, cart_name: str, cart_items: List[ItemInDB]) -> dict:
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
    # Product listing with clickable images
    items_html = "".join([
    f"""
    <div style="display: flex; align-items: center; padding: 10px 15px; border-bottom: 1px solid #ddd; margin: 0;">
        <a href="{item.url or '#'}" target="_blank" style="text-decoration: none;">
            <img src="{item.image or ''}" alt="{item.name}" style="width: 70px; height: 70px; border-radius: 8px; margin-right: 12px;">
        </a>
        <div>
            <h3 style="margin: 0; padding: 0; color: #333; font-size: 16px; line-height: 1.2; display: block;">
                <a href="{item.url or '#'}" target="_blank" style="text-decoration: none; color: inherit;">{item.name}</a>
            </h3>
            <p style="margin: 3px 0 0 0; padding: 0; font-size: 14px; color: #666; line-height: 1.2; display: block;">{item.price}</p>
            {"<p style='font-size: 13px; color: #888; font-style: italic; margin: 3px 0 0 0; padding: 0; line-height: 1.2; display: block;'>Note: " + item.notes + "</p>" if item.notes else ""}
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

    # Use AWS SES instead of Gmail SMTP
    return await send_email_ses(recipient_email, subject, body_html)


# USER FUNCTIONS --------------------------------------------------------------------------------------------------------------
async def add_user_by_email(email: str, name: str = "Unknown") -> dict:
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