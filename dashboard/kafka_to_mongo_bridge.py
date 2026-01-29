from kafka import KafkaConsumer
import pymongo
import json
import time

# CONFIG
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9093'
TOPIC = 'movie_ratings'
MONGO_URI = "mongodb://admin:password@localhost:27017/"
DB_NAME = "movie_db"
COLLECTION_NAME = "live_ratings"

def main():
    print("🚀 Starting Bridge: Kafka -> MongoDB...")
    
    # Kafka Consumer
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest'
    )
    
    # Mongo Connection
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print("Listening for messages...")
    
    for message in consumer:
        data = message.value
        
        # Insert vào MongoDB
        collection.insert_one(data)
        
        title = data.get('title', 'Unknown')
        print(f"saved to Mongo: {title}", flush=True)

if __name__ == "__main__":
    main()
