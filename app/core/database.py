from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Initialize MongoDB client with connection pooling
# maxPoolSize: Maximum number of connections in the pool (default: 100)
# minPoolSize: Minimum number of connections in the pool (default: 0)
# maxIdleTimeMS: Close connections after this many milliseconds of inactivity (default: None)
client = AsyncIOMotorClient(
    settings.MONGO_URL,
    maxPoolSize=50,  # Reasonable pool size for small to medium traffic
    minPoolSize=5,   # Keep some connections ready
    maxIdleTimeMS=45000,  # Close idle connections after 45 seconds
    serverSelectionTimeoutMS=5000,  # Timeout for server selection
    connectTimeoutMS=10000,  # Timeout for initial connection
)
db = client["buyHive"]

# Collections (3-collection model, 2-extra-collections)
users_collection = db["users"]
carts_collection = db["carts"]
items_collection = db["items"]
feedback_collection = db["feedback"]
failed_extraction_collection = db["failed_extractions"]

