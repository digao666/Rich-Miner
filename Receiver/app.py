import connexion
import requests
from connexion import NoContent
import json
import yaml
import logging.config
import uuid


MAX_EVENTS = 10
EVENT_FILE = 'event.json'

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('receiver')


def report_temperature(body):
    """ Receives a hardware temperature """
    trace_id = uuid.uuid1()
    body['trace_id'] = f'{trace_id}'
    payload = json.dumps(body)
    url = app_config['eventstore1']['url']

    event_receipt = f'Received event report temperature request with a trace id of {trace_id}'
    logger.info(event_receipt)

    r = requests.post(url, data=payload, headers={"Content-Type": "application/json"})

    return_receipt = f'Returned event report temperature response (Id: {trace_id}) with status {r.status_code}'
    logger.info(return_receipt)

    return NoContent, r.status_code


def report_fan_speed(body):
    """ Receives a fan speed """
    trace_id = uuid.uuid1()
    body['trace_id'] = f'{trace_id}'
    payload = json.dumps(body)
    url = app_config['eventstore2']['url']

    event_receipt = f'Received event report fan speed request with a trace id of {trace_id}'
    logger.info(event_receipt)

    r = requests.post(url, data=payload, headers={"Content-Type": "application/json"})

    return_receipt = f'Returned event report fan speed response (Id: {trace_id}) with status {r.status_code}'
    logger.info(return_receipt)

    return NoContent, r.status_code


app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
