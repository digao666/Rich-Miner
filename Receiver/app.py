import connexion
import requests
from connexion import NoContent
import datetime
from datetime import datetime
import json
import os
import yaml
import logging
import logging.config
import uuid


logger = logging.getLogger('basicLogger')
MAX_EVENTS = 10
EVENT_FILE = 'event.json'

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


# def write_request(body):
#     """ add request body to json """
#     if os.path.isfile(EVENT_FILE):
#         with open(EVENT_FILE, "r+") as file1:
#             file_content = json.load(file1)
#     else:
#         file_content = []
#     if 'fan_speed' in body:
#         formatted_object = {
#             "received_timestamp": str(datetime.now()),
#             "request_data": str(
#                 f"The GPU {body['ming_card_id']} of ming rig {body['ming_rig_id']}'s {body['fan_speed']['fan_position']}"
#                 f" fan speed is {body['fan_speed']['fan_speed']}")
#         }
#     else:
#         formatted_object = {
#             "received_timestamp": str(datetime.now()),
#             "request_data": str(f"The GPU {body['ming_card_id']} of ming rig {body['ming_rig_id']}'s core "
#                                 f"temperature is {body['temperature']['core_temperature']}")
#         }
#     file_content.append(formatted_object)
#
#     if len(file_content) > MAX_EVENTS:
#         file_content.pop(0)
#     json_object = json.dumps(file_content, indent=4)
#
#     with open(EVENT_FILE, "w+") as file2:
#         file2.write(json_object)
#     return json_object


def report_temperature(body):
    """ Receives a hardware temperature """
    # write_request(body)
    temperature_id = uuid.uuid1()
    body['id'] = f'{temperature_id}'
    payload = json.dumps(body)
    url = app_config['eventstore1']['url']
    event_receipt = f'Received event report temperature request with a trace id of {temperature_id}'
    logging.info(event_receipt)

    r = requests.post(url, data=payload, headers={"Content-Type": "application/json"})

    return_receipt = f'Returned event report temperature response (Id: {temperature_id}) with status {r.status_code}'
    logging.info(return_receipt)

    return NoContent, r.status_code


def report_fan_speed(body):
    """ Receives a fan speed """
    # write_request(body)
    fan_speed_id = uuid.uuid1()
    body['id'] = f'{fan_speed_id}'
    payload = json.dumps(body)
    url = app_config['eventstore2']['url']

    event_receipt = f'Received event report fan speed request with a trace id of {fan_speed_id}'
    logging.info(event_receipt)
    print(event_receipt)

    r = requests.post(url, data=payload, headers={"Content-Type": "application/json"})

    return_receipt = f'Returned event report fan speed response (Id: {fan_speed_id}) with status {r.status_code}'
    logging.info(return_receipt)
    print(return_receipt)

    return NoContent, r.status_code


app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
