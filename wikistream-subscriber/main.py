import json
import logging
import time
from json.decoder import JSONDecodeError
from dataclasses import dataclass, asdict

from sseclient import SSEClient
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# Configuration
BOOTSTRAP_SERVER='kafka:9093'
TOPIC='wiki-stream'
WIKI_STREAM='https://stream.wikimedia.org/v2/stream/recentchange'

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def create_producer(bootstrap_server: str, retries: int = 5, delay: int = 5) -> KafkaProducer:
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_server,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            if producer.bootstrap_connected():
                logging.info(f'Connected to Kafka broker at {bootstrap_server}')
                return producer
        
        except NoBrokersAvailable:
            logging.warning(f'Kafka broker at {bootstrap_server} unavailable (attempt {attempt+1}/{retries})')
            time.sleep(delay)
        
    logging.error(f'Failed to connect to Kafka broker at {bootstrap_server} after {retries} attempts')
    exit(1)


@dataclass
class WikiEvent:
    title: str
    title_url: str
    type: str
    user: str
    comment: str
    timestamp: int
    
    @classmethod
    def from_json(cls, event_json: dict):
        return cls(
            title=event_json['title'],
            title_url=event_json['title_url'],
            type=event_json['type'],
            user=event_json['user'],
            comment=event_json['comment'],
            timestamp=event_json['timestamp']
        )
        
def should_ignore(event_json) -> bool:
    return any([
        event_json['bot'],
        event_json['type'] != 'edit',
        event_json['namespace'] != 0,
        'en.wikipedia.org' not in event_json['meta']['uri']
    ])

def is_valid_json(data: str) -> bool:
    return data.startswith('{') and data.endswith('}')

def main():
    producer = create_producer(BOOTSTRAP_SERVER)
    
    for event in SSEClient(WIKI_STREAM):
        raw_data = event.data.strip()
        if not raw_data or not is_valid_json(raw_data):
           continue # Ignore malformed events early
            
        try:
            event_json = json.loads(event.data)
            if should_ignore(event_json):
                continue
            
            wiki_event = WikiEvent.from_json(event_json)
            producer.send(TOPIC, asdict(wiki_event))
            logging.info(f"Sent event to topic '{TOPIC}': {wiki_event.title}")
        
        except (TypeError, JSONDecodeError, KeyError) as e:
            logging.error(f"Malformed JSON: {event.data}", exc_info=True)
        except Exception as e:
            logging.error(f"Unhandled error: {e}", exc_info=True)

if __name__ == '__main__':
    main()