import asyncio
from app.services.email.email_service import send_email_ses, check_ses_availability

async def test_ses():
    status = check_ses_availability()
    
    if status["status"] != "ok":
        raise Exception("❌ SES is not properly configured!")
        return
    
    result = await send_email_ses(
        recipient_email="gbelaunderojas@gmail.com",  # Use YOUR email address
        subject="Test Email from BuyHive SES",
        html_body="""
        <html>
        <body>
            <h1>Hello from BuyHive!</h1>
            <p>This is a test email sent via AWS SES.</p>
            <p>If you're seeing this, SES is working! 🎉</p>
        </body>
        </html>
        """,
        text_body="Hello from BuyHive! This is a test email sent via AWS SES."
    )
    
    if "error" in result:
        raise Exception(f"❌ Error: {result['error']}")
    else:
        raise Exception(f"✅ Success! Message ID: {result.get('message_id')}")

if __name__ == "__main__":
    asyncio.run(test_ses())

