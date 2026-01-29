import pymongo
import random
import time
from datetime import datetime

# Config
MONGO_URI = "mongodb://admin:password@localhost:27017/"
DB_NAME = "movie_db"
COLLECTION_NAME = "live_ratings"

def main():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print("Seeding data directly to MongoDB to test Dashboard...")
    
    try:
        while True:
            rating = {
                "user_id": random.randint(1, 1000),
                "movie_id": random.randint(1, 20), # Limit to 20 movies for better chart viz
                "rating": random.randint(1, 5),
                "timestamp": datetime.utcnow().isoformat()
            }
            collection.insert_one(rating)
            print(f"Inserted to Mongo: {rating}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped seeding.")

if __name__ == "__main__":
    main()
