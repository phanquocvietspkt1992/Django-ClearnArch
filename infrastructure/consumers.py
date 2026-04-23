"""
Kafka consumer entrypoint. Run with:
    python -m infrastructure.consumers
"""
import json
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings
from confluent_kafka import Consumer, KafkaError
from apps.notifications import services as notification_services

TOPICS = ['order-created', 'product-created']


def _handle(topic, payload):
    if topic == 'order-created':
        notification_services.create_order_notification(
            user_id=payload['user_id'],
            order_id=payload['id'],
            total_price=payload['total_price'],
        )
    elif topic == 'product-created':
        notification_services.create_product_notification(
            product_id=payload['id'],
            product_name=payload['name'],
            price=payload['price'],
        )


def run():
    consumer = Consumer({
        'bootstrap.servers': settings.KAFKA['BOOTSTRAP_SERVERS'],
        'group.id': 'notifications-consumer',
        'auto.offset.reset': 'earliest',
    })
    consumer.subscribe(TOPICS)
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f'Kafka error: {msg.error()}')
                continue
            try:
                payload = json.loads(msg.value().decode('utf-8'))
                _handle(msg.topic(), payload)
            except Exception as e:
                print(f'Failed to process message: {e}')
    finally:
        consumer.close()


if __name__ == '__main__':
    run()
