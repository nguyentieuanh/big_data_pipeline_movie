import requests
import json
import time
import random
from kafka import KafkaProducer

# CONFIG NO KEY REQUIRED
API_URL = "https://api.tvmaze.com/schedule" # Lấy lịch chiếu phim hôm nay
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9093'
TOPIC = 'movie_ratings'

def get_real_movies():
    try:
        # Lấy lịch chiếu hôm nay tại US (data luôn tươi mới)
        response = requests.get(API_URL, params={"country": "US"})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print(f"🎬 Starting Real Movie Producer (Source: TVMaze - No Key)...")
    
    while True:
        shows = get_real_movies()
        if not shows:
            print("No shows found. Retrying...")
            time.sleep(5)
            continue
            
        random.shuffle(shows) # Xáo trộn để stream ngẫu nhiên
        
        for item in shows:
            show_info = item.get('show', {})
            
            # Tạo event rating giả lập cho show thật
            event = {
                "movie_id": show_info.get('id'),
                "title": show_info.get('name'),
                "genre": show_info.get('genres'),
                "rating": show_info.get('rating', {}).get('average') or random.randint(5, 10), # Nếu không có rating thì random
                "network": (show_info.get('network') or {}).get('name') or "Unknown Network",
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "source": "tvmaze_api"
            }
            
            # Gửi vào Kafka
            producer.send(TOPIC, event)
            print(f"Sent: {event['title']} ({event['network']}) - Rating: {event['rating']}", flush=True)
            
            # Giả lập tốc độ stream
            time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    main()
