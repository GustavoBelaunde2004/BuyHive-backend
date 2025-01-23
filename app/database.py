from motor.motor_asyncio import AsyncIOMotorClient

#Username: gabelaunde
#Password: yspXX6hlEWxIYBmK

# MongoDB connection URI
MONGO_URI = "mongodb+srv://gabelaunde:yspXX6hlEWxIYBmK@buyhive-testcluster.qstpq.mongodb.net/?retryWrites=true&w=majority&appName=BuyHive-TestCluster"

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client["buyHive"]
cart_collection = db["cartItems"]
