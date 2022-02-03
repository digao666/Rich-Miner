import connexion
import requests
from connexion import NoContent
import datetime
from datetime import datetime
import json
import os

MAX_EVENTS = 10
EVENT_FILE = 'event.json'


def write_request(body):
    """ add request body to json """
    if os.path.isfile(EVENT_FILE):
        with open(EVENT_FILE, "r+") as file1:
            file_content = json.load(file1)
    else:
        file_content = []
    if 'fan_speed' in body:
        formatted_object = {
            "received_timestamp": str(datetime.now()),
            "request_data": str(
                f"The GPU {body['ming_card_id']} of ming rig {body['ming_rig_id']}'s {body['fan_speed']['fan_position']}"
                f" fan speed is {body['fan_speed']['fan_speed']}")
        }
    else:
        formatted_object = {
            "received_timestamp": str(datetime.now()),
            "request_data": str(f"The GPU {body['ming_card_id']} of ming rig {body['ming_rig_id']}'s core "
                                f"temperature is {body['temperature']['core_temperature']}")
        }
    file_content.append(formatted_object)

    if len(file_content) > MAX_EVENTS:
        file_content.pop(0)
    json_object = json.dumps(file_content, indent=4)

    with open(EVENT_FILE, "w+") as file2:
        file2.write(json_object)
    return json_object


def report_temperature(body):
    """ Receives a hardware temperature """
    # write_request(body)
    payload = json.dumps(body)
    url = 'http://192.168.86.218:8090/status/temperature'
    r = requests.post(url, data=payload, headers={"Content-Type": "application/json"})
    return NoContent, r.status_code


def report_fan_speed(body):
    """ Receives a fan speed """
    # write_request(body)
    payload = json.dumps(body)
    url = 'http://192.168.86.218:8090/status/fanspeed'
    r = requests.post(url, data=payload, headers={"Content-Type": "application/json"})
    return NoContent, r.status_code


app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
