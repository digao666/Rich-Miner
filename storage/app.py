import connexion
import datetime
import logging.config
import yaml
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pykafka.common import OffsetType
from pykafka import KafkaClient
from threading import Thread
from base import Base
from fan_speed import FanSpeed
from temperature import Temperature
from sqlalchemy import and_
import time
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
logger = logging.getLogger('storage')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

user = app_config['datastore']['user']
password = app_config['datastore']['password']
port = app_config['datastore']['port']
hostname = app_config['datastore']['hostname']
db = app_config['datastore']['db']


def get_health():
    return 200


# connect to kafka
host_name = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
max_retry = app_config["events"]["retry"]
retry = 0
while retry < max_retry:
    logger.info(f"Try to connect Kafka Server, this is number {retry} try")
    try:
        client = KafkaClient(hosts=host_name)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        logger.info("Successfully connect to Kafka")
        consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False,
                                            auto_offset_reset=OffsetType.LATEST)
        break
    except:
        logger.error(f"Failed to connect to Kafka, this is number {retry} try")
        time.sleep(app_config["events"]["sleep"])
        retry += 1
        logger.info("retry in 10 second")


DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')
logger.info(f"Connecting to DB. Hostname:{hostname}, Port:{port}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_temperature(start_timestamp, end_timestamp):
    """ Gets new temperature after the timestamp """
    session = DB_SESSION()
    readings = session.query(Temperature).filter(
        and_(Temperature.date_created >= start_timestamp,
             Temperature.date_created < end_timestamp))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for Temperature readings between %s and %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))
    return results_list, 200


def get_fan_speed(start_timestamp, end_timestamp):
    """ Gets new fan speed after the timestamp """
    session = DB_SESSION()
    readings = session.query(FanSpeed).filter(
        and_(FanSpeed.date_created >= start_timestamp,
             FanSpeed.date_created < end_timestamp))

    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()
    logger.info("Query for fan speed readings between %s and %s returns %d results" %
                (start_timestamp, end_timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]

        session = DB_SESSION()
        data = {}
        if msg["type"] == "temperature":
            data = Temperature(payload['trace_id'],
                            payload['date_created'],
                            payload['ming_rig_id'],
                            payload['ming_card_id'],
                            payload['timestamp'],
                            payload['temperature']['core_temperature'],
                            payload['temperature']['shell_temperature'])

        elif msg["type"] == "fanspeed":
            data = FanSpeed(payload['trace_id'],
                            payload['date_created'],
                            payload['ming_rig_id'],
                            payload['ming_card_id'],
                            payload['timestamp'],
                            payload['fan_speed']['fan_speed'],
                            payload['fan_speed']['fan_size'])


        session.add(data)
        session.commit()
        session.close()
        logger.debug(f'Stored event {msg["type"]} request with a trace id of {payload["trace_id"]}')
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/storage", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()
    app.run(port=8090, debug=True)
