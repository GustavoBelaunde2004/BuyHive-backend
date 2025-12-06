from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

# Initialize MongoDB client
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client["buyHive"]
cart_collection = db["cartItems"]
