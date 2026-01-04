"""User service for business logic."""
from typing import List, Dict
from app.services.item_service import ItemService
from app.repositories.cart_repository import CartRepository
from app.models.item import ItemInDB
from app.services.email.email_service import send_email_ses


class UserService:
    """Service for user business logic."""
    
    def __init__(self, item_service: ItemService, cart_repo: CartRepository):
        """
        Initialize user service with item service and cart repository.
        
        Args:
            item_service: Item service instance
            cart_repo: Cart repository instance
        """
        self.item_service = item_service
        self.cart_repo = cart_repo
    
    async def share_cart(
        self,
        user_id: str,
        cart_id: str,
        recipient_email: str,
        sender_name: str,
        sender_email: str
    ) -> Dict:
        """
        Share a cart by sending its details via email.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            recipient_email: Recipient email address
            sender_name: Sender name
            sender_email: Sender email
            
        Returns:
            Dictionary with success message
            
        Raises:
            ValueError: If cart not found
        """
        # Get cart to get cart name
        cart_doc = await self.cart_repo.find_by_id(user_id, cart_id)
        if not cart_doc:
            raise ValueError("Cart not found!")
        
        cart_name = cart_doc.get("cart_name", "Cart")
        
        # Get cart items
        cart_items: List[ItemInDB] = await self.item_service.get_cart_items(user_id, cart_id)
        
        # Send email
        return await self.send_cart_email(
            recipient_email,
            cart_name,
            cart_items,
            sender_name,
            sender_email
        )
    
    async def send_cart_email(
        self,
        recipient_email: str,
        cart_name: str,
        cart_items: List[ItemInDB],
        sender_name: str = "A BuyHive user",
        sender_email: str = ""
    ) -> Dict:
        """
        Send cart details via email.
        
        Args:
            recipient_email: Recipient email address
            cart_name: Cart name
            cart_items: List of items in cart
            sender_name: Sender name
            sender_email: Sender email
            
        Returns:
            Dictionary with result
        """
        subject = f"{sender_name} shared a cart with you: {cart_name}"
        
        # Generate items HTML
        items_html = "".join([
            f"""
                                        <tr>
                                            <td style="padding: 16px 0; border-bottom: 1px solid #e5e5e5;">
                                                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                                    <tr>
                                                        <td style="width: 100px; padding-right: 16px; vertical-align: top;">
                                                            <a href="{item.url or '#'}" target="_blank" style="text-decoration: none;">
                                                                <img src="{item.image or 'https://via.placeholder.com/100?text=No+Image'}" 
                                                                     alt="{item.name}" 
                                                                     style="width: 100px; height: 100px; object-fit: cover; border-radius: 4px; display: block;">
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
        
        # Email HTML template
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
        
        return await send_email_ses(recipient_email, subject, body_html)

