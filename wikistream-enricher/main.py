import logging
from json.decoder import JSONDecodeError

from wikipedia_api import fetch_wikiprojects
from kafka_utils import init_kafka_consumer, init_kafka_producer
from config import BOOTSTRAP_SERVER, INPUT_TOPIC, OUTPUT_TOPIC, DLQ_TOPIC, GROUP_ID

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def add_wikiprojects_to_event(event: dict) -> dict:
    title = event.get('title')
    wikiprojects = fetch_wikiprojects(title)
    if not wikiprojects:
        logging.info(f'No WikiProject data found for {title}')
        return None

    event['wikiprojects'] = wikiprojects
    return event

def main():
    producer = init_kafka_producer(BOOTSTRAP_SERVER)
    consumer = init_kafka_consumer(BOOTSTRAP_SERVER, INPUT_TOPIC, GROUP_ID)
    logging.info(f"Subscribed to topic '{INPUT_TOPIC}', publishing to '{OUTPUT_TOPIC}'")

    for message in consumer:
        try:
            event = add_wikiprojects_to_event(message.value)
            if event:
                producer.send(OUTPUT_TOPIC, event)
                logging.info(f"Published enriched event for: {event['title']} (offset={message.offset})")

        except (JSONDecodeError, KeyError, TypeError) as e:
            logging.warning(f"Invalid event: {message.value} - Sending to Dead Letter Queue '{DLQ_TOPIC}'", exc_info=True)
            producer.send(DLQ_TOPIC, message.value)

        except Exception as e:
            logging.error(f'Unhandled error: {e}')

        finally:
            consumer.commit() # Manual offset commit to avoid reprocessing malformed events

if __name__ == '__main__':
    main()