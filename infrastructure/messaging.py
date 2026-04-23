import json
import uuid
from django.conf import settings

_producer = None


def _get_producer():
    global _producer
    if _producer is None:
        from confluent_kafka import Producer
        _producer = Producer({'bootstrap.servers': settings.KAFKA['BOOTSTRAP_SERVERS']})
    return _producer


def publish_message(topic, message):
    try:
        producer = _get_producer()
        producer.produce(
            topic,
            key=str(uuid.uuid4()),
            value=json.dumps(message).encode('utf-8'),
        )
        producer.flush()
    except Exception:
        pass  # fire-and-forget — don't block if Kafka is unavailable
