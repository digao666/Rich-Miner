from pykafka import KafkaClient
from flask_cors import CORS, cross_origin
import logging.config
import yaml
import json
import connexion
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('audit')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

def get_temperature_reading(index):
    """ Get TEMP Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving TEMP at index %d" % index)
    temp_list = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'temperature':
                temp_list.append(msg['payload'])
        return temp_list[index], 200
    except:
        logger.error("No more messages found")

    logger.error("Could not find TEMP at index %d" % index)
    return {"message": "Not Found"}, 404


def get_fan_speed_reading(index):
    """ Get fs Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving FS at index %d" % index)
    fanspeed_list = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'fanspeed':
                fanspeed_list.append(msg['payload'])
        return fanspeed_list[index], 200
    except:
        logger.error("No more messages found")

    logger.error("Could not find FS at index %d" % index)
    return {"message": "Not Found"}, 404


def get_health():
    return 200


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/audit_log", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    get_health()

    app.run(port=8110)
