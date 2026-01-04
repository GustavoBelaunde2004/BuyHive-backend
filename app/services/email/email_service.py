"""
AWS SES email service for sending emails.
Replaces yagmail (Gmail SMTP) with AWS SES for better scalability.
"""
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from typing import Optional

# Initialize SES client
ses_client = None
if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
    ses_client = boto3.client(
        'ses',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

async def send_email_ses(
    recipient_email: str, 
    subject: str, 
    html_body: str,
    text_body: Optional[str] = None
) -> dict:
    """
    Send an email using AWS SES.
    
    Args:
        recipient_email: Email address of the recipient
        subject: Email subject line
        html_body: HTML content of the email
        text_body: Optional plain text version of the email
        
    Returns:
        dict with "message" and optionally "message_id" on success,
        or dict with "error" on failure
    """
    if not ses_client:
        return {
            "error": "AWS SES not configured. Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and SES_FROM_EMAIL in your .env file."
        }
    
    if not settings.SES_FROM_EMAIL:
        return {
            "error": "SES_FROM_EMAIL not configured. Please set it in your .env file."
        }
    
    try:
        message = {
            'Subject': {'Data': subject},
            'Body': {'Html': {'Data': html_body}}
        }
        
        # Add text body if provided
        if text_body:
            message['Body']['Text'] = {'Data': text_body}
        
        response = ses_client.send_email(
            Source=settings.SES_FROM_EMAIL,
            Destination={'ToAddresses': [recipient_email]},
            Message=message
        )
        
        return {
            "message": "Email sent successfully!",
            "message_id": response['MessageId']
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        # Handle common SES errors
        if error_code == 'MessageRejected':
            return {
                "error": f"Email rejected: {error_message}. Please verify the recipient email address."
            }
        elif error_code == 'MailFromDomainNotVerified':
            return {
                "error": f"Sender domain not verified: {error_message}. Please verify your SES domain or email address."
            }
        else:
            return {
                "error": f"AWS SES error ({error_code}): {error_message}"
            }
    except Exception as e:
        return {
            "error": f"Unexpected error sending email: {str(e)}"
        }

def check_ses_availability() -> dict:
    """Check if AWS SES is configured and available."""
    if not ses_client:
        return {
            "status": "unavailable",
            "message": "AWS SES not configured. Please set AWS credentials in .env file."
        }
    
    if not settings.SES_FROM_EMAIL:
        return {
            "status": "unavailable",
            "message": "SES_FROM_EMAIL not configured."
        }
    
    return {
        "status": "ok",
        "message": "AWS SES configured and ready",
        "from_email": settings.SES_FROM_EMAIL
    }

