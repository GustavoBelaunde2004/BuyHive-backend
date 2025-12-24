from typing import List
from app.config.settings import settings
from .database import users_collection
from app.models.item import ItemInDB
from app.services.email_service import send_email_ses

async def send_email_gmail(
    recipient_email: str, 
    cart_name: str, 
    cart_items: List[ItemInDB],
    sender_name: str = "A BuyHive user",
    sender_email: str = ""
) -> dict:
    """Send a minimal, professional email with cart details and sender information."""
    subject = f"{sender_name} shared a cart with you: {cart_name}"

    # Generate items HTML separately to avoid f-string syntax issues
    items_html = "".join([
        f"""
                                        <tr>
                                            <td style="padding: 16px 0; border-bottom: 1px solid #e5e5e5;">
                                                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                                    <tr>
                                                        <td style="width: 80px; padding-right: 16px; vertical-align: top;">
                                                            <a href="{item.url or '#'}" target="_blank" style="text-decoration: none;">
                                                                <img src="{item.image or 'https://via.placeholder.com/80?text=No+Image'}" 
                                                                     alt="{item.name}" 
                                                                     style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px; display: block;">
                                                            </a>
                                                        </td>
                                                        <td style="vertical-align: top;">
                                                            <a href="{item.url or '#'}" target="_blank" style="text-decoration: none; color: inherit;">
                                                                <h3 style="margin: 0 0 4px; font-size: 16px; font-weight: 500; color: #1a1a1a; line-height: 1.4;">
                                                                    {item.name}
                                                                </h3>
                                                            </a>
                                                            <p style="margin: 0 0 4px; font-size: 15px; font-weight: 600; color: #1a1a1a;">
                                                                {item.price}
                                                            </p>
                                                            {f'<p style="margin: 4px 0 0; font-size: 13px; color: #888; font-style: italic; line-height: 1.4;">Note: {item.notes}</p>' if item.notes else ''}
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        """ for item in cart_items
    ])

    # Minimal, professional email design
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
        <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f5f5f5;">
            <tr>
                <td style="padding: 40px 20px;">
                    <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 32px 32px 24px; text-align: center; border-bottom: 1px solid #e5e5e5;">
                                <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #1a1a1a;">BuyHive</h1>
                            </td>
                        </tr>
                        
                        <!-- Sender Info -->
                        <tr>
                            <td style="padding: 24px 32px 16px;">
                                <p style="margin: 0; font-size: 14px; color: #666; line-height: 1.5;">
                                    <strong style="color: #1a1a1a;">{sender_name}{f' ({sender_email})' if sender_email else ''}</strong> shared a cart with you:
                                </p>
                                <h2 style="margin: 8px 0 0; font-size: 20px; font-weight: 600; color: #1a1a1a;">{cart_name}</h2>
                            </td>
                        </tr>
                        
                        <!-- Items List -->
                        <tr>
                            <td style="padding: 0 32px 24px;">
                                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                    {items_html}
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 24px 32px; background-color: #f9f9f9; border-top: 1px solid #e5e5e5; border-radius: 0 0 8px 8px; text-align: center;">
                                <p style="margin: 0; font-size: 12px; color: #999; line-height: 1.5;">
                                    Sent via BuyHive 🐝
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    # Use AWS SES instead of Gmail SMTP
    return await send_email_ses(recipient_email, subject, body_html)


# USER FUNCTIONS --------------------------------------------------------------------------------------------------------------
async def add_user_by_email(email: str, name: str = "Unknown") -> dict:
    """Add a new user to the database or ensure they already exist."""
    existing_user = await users_collection.find_one({"email": email})
    if existing_user:
        return {"message": "User already exists!"}

    new_user = {
        "user_id": f"email|{email}",  # legacy helper: stable id not available here
        "email": email,
        "name": name,
        "cart_count": 0,
        "cart_ids": [],
    }
    await users_collection.insert_one(new_user)
    return {"message": "User added successfully!"}