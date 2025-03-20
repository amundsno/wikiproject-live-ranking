import json
import logging

from flask import Flask, Response
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Configuration
BOOTSTRAP_SERVER='kafka:9093'
TOPIC='wiki-stream-enriched'

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

class KafkaSseStreamer:
    def __init__(self, bootstrap_server: str, topic: str):
        self.bootstrap_server = bootstrap_server
        self.topic = topic

    def _create_consumer(self) -> KafkaConsumer:
        try:
            return KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_server,
                auto_offset_reset="latest",
                enable_auto_commit=False,
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
        except KafkaError as e:
            logging.error(f"Kafka connection error: {e}", exc_info=True)
            return None

    def event_stream(self):
        """Generator that yields Kafka messages as SSE events"""
        consumer = self._create_consumer()
        if not consumer:
            yield "retry: 5000\n\n"
            return

        try:
            for message in consumer:
                event = message.value
                yield f"data: {json.dumps(event)}\n\n"
        except GeneratorExit:
            logging.info('SSE stream closed by client')
        finally:
            consumer.close()


app = Flask(__name__)

streamer = KafkaSseStreamer(BOOTSTRAP_SERVER, TOPIC)

@app.route('/events')
def sse():
    return Response(streamer.event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005, threaded=True)