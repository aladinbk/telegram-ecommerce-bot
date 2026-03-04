from pymongo import MongoClient
from app.config import MONGO_URI

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client["telegram_shop"]

products_collection = db["products"]
orders_collection = db["orders"]