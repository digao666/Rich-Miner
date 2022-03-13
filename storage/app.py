import connexion
import datetime
import logging.config
import yaml
import json
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pykafka.common import OffsetType
from pykafka import KafkaClient
from threading import Thread
from base import Base
from fan_speed import FanSpeed
from temperature import Temperature

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('storage')
user = app_config['datastore']['user']
password = app_config['datastore']['password']
port = app_config['datastore']['port']
hostname = app_config['datastore']['hostname']
db = app_config['datastore']['db']
DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')
logger.info(f"Connecting to DB. Hostname:{hostname}, Port:{port}")

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_temperature(timestamp):
    """ Gets new temperature after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(Temperature).filter(Temperature.date_created >= timestamp_datetime)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for Temperature readings after %s returns %d results" %
                (timestamp, len(results_list)))
    return results_list, 200


def get_fan_speed(timestamp):
    """ Gets new fan speed after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(FanSpeed).filter(FanSpeed.date_created >= timestamp_datetime)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for fan speed readings after %s returns %d results" %
                (timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    """ Process event messages """
    host_name = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=host_name)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
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
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()
    app.run(port=8090, debug=True)

