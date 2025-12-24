import asyncio
from app.services.email_service import send_email_ses, check_ses_availability

async def test_ses():
    # First, check if SES is configured
    print("Checking SES configuration...")
    status = check_ses_availability()
    print(f"Status: {status}\n")
    
    if status["status"] != "ok":
        print("❌ SES is not properly configured!")
        return
    
    # Test sending an email
    print("Sending test email...")
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
    
    print(f"Result: {result}")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success! Message ID: {result.get('message_id')}")

if __name__ == "__main__":
    asyncio.run(test_ses())

