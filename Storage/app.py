import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from fan_speed import FanSpeed
from temperature import Temperature
import yaml
import logging.config
import datetime

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

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def report_temperature(body):
    """ Receives a hardware temperature """
    session = DB_SESSION()
    temp = Temperature(body['trace_id'],
                       body['date_created'],
                       body['ming_rig_id'],
                       body['ming_card_id'],
                       body['timestamp'],
                       body['temperature']['core_temperature'],
                       body['temperature']['shell_temperature'])
    session.add(temp)
    session.commit()
    session.close()
    trace_id = body['trace_id']
    logger.debug(f'Stored event temperature request with a trace id of {trace_id}')
    return NoContent, 201


def report_fan_speed(body):
    """ Receives a fan speed """
    session = DB_SESSION()
    fs = FanSpeed(body['trace_id'],
                  body['date_created'],
                  body['ming_rig_id'],
                  body['ming_card_id'],
                  body['timestamp'],
                  body['fan_speed']['fan_size'],
                  body['fan_speed']['fan_speed'])
    session.add(fs)
    session.commit()
    session.close()
    trace_id = body['trace_id']
    logger.debug(f'Stored event fan speed request with a trace id of {trace_id}')
    return NoContent, 201


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


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090, debug=True)
