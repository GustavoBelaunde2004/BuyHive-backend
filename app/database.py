from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db = client["buyHive"]
cart_collection = db["cartItems"]
