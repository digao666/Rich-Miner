import connexion
import datetime
import json
import logging.config
import uuid
import yaml
from pykafka import KafkaClient
from connexion import NoContent
import time

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('receiver')

kafka_server = app_config['events']['hostname']
kafka_port = app_config['events']['port']
kafka_topic = app_config['events']['topic']


def report_temperature(body):
    """ Receives a hardware temperature """
    trace_id = uuid.uuid1()
    body['trace_id'] = f'{trace_id}'
    body['date_created'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    event_receipt = f'Received event report temperature request with a trace id of {trace_id}'
    logger.info(event_receipt)

    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[str.encode(f'{kafka_topic}')]
    producer = topic.get_sync_producer()
    msg = {"type": "temperature",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return_receipt = f'Returned event report temperature response (Id: {trace_id}) with status 201'
    logger.info(return_receipt)

    return NoContent, 201


def report_fan_speed(body):
    """ Receives a fan speed """
    trace_id = uuid.uuid1()
    body['trace_id'] = f'{trace_id}'
    body['date_created'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(body['date_created'])

    event_receipt = f'Received event report fan speed request with a trace id of {trace_id}'
    logger.info(event_receipt)

    client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
    topic = client.topics[str.encode(f'{kafka_topic}')]
    producer = topic.get_sync_producer()
    msg = {"type": "fanspeed",
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%SZ"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return_receipt = f'Returned event report fan speed response (Id: {trace_id}) with status 201'
    logger.info(return_receipt)

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
