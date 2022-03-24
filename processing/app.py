import connexion
import logging.config
import requests
import yaml
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS
from base import Base
from stats import Stats
import os
import os.path
from os import path
from create_table import create_database

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
logger = logging.getLogger('processing')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

def check_data():
    if path.exists(f'{app_config["datastore"]["filename"]}'):
        logger.info(f'log path is {app_config["datastore"]["filename"]}')
        logger.info("data.sqlite is exist")
    else:
        logger.info("data.sqlite is not exist")
        create_database()
        logger.info("create data.sqlite")

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    """ Gets the temperature and fan speed events stats  """
    session = DB_SESSION()
    logger.info("Start Get Stats request")
    stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if not stats:
        logger.debug(f'No latest statistics found')
        return "Statistics do not exist", 404
    stats = stats.to_dict()
    session.close()
    logger.debug(f'The latest statistics is {stats}')
    logger.info("Get Stats request done")
    return stats, 200


def populate_stats(dictionary=None):
    """ Periodically update stats """
    logger.info("Start Periodic Processing")
    session = DB_SESSION()
    stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if not stats:
        stats = {
            "num_shell_temp": 0,
            "num_core_temp": 0,
            "num_fan_speed": 0,
            "max_fan_speed": 0,
            "max_shell_temp": 0,
            "max_core_temp": 0,
            "last_updated": datetime.datetime.now()
        }

    logger.info(stats)
    if not isinstance(stats, dict):
        stats = stats.to_dict()

    new_stats = {
        "num_shell_temp": 0,
        "num_core_temp": 0,
        "num_fan_speed": 0,
        "max_fan_speed": 0,
        "max_shell_temp": 0,
        "max_core_temp": 0,
        "last_updated": datetime.datetime.now()
    }

    start_timestamp = stats['last_updated']
    logger.debug(start_timestamp)
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    logger.debug(current_timestamp)

    # Temperature
    temperature_response = requests.get(app_config["eventstore"]["url"] +
                                        "/status/temperature?start_timestamp=" +
                                        f"{start_timestamp}" + "&end_timestamp=" +
                                        f"{current_timestamp}")

    if temperature_response.status_code != 200:
        logger.error('get_temperature - Invalid request')
    else:
        temperature_response_data = temperature_response.json()
        logger.info(
            f"Total number of new temperatures is: {len(temperature_response_data)}")
        new_stats['num_core_temp'] = stats['num_core_temp'] + len(temperature_response_data)
        new_stats['num_shell_temp'] = stats['num_shell_temp'] + len(temperature_response_data)
        max_shell_temp = stats['max_shell_temp']
        max_core_temp = stats['max_core_temp']
        for item in temperature_response_data:
            max_shell_temp = max(max_shell_temp, item['temperature']['shell_temperature'])
            max_core_temp = max(max_core_temp, item['temperature']['core_temperature'])
            # logger.debug(f'Temperature event {item["trace_id"]} processed')
        new_stats['max_shell_temp'] = max_shell_temp
        new_stats['max_core_temp'] = max_core_temp

    # fan speed
    fan_speed_response = requests.get(app_config["eventstore"]["url"] +
                                      "/status/fanspeed?start_timestamp=" +
                                      f"{start_timestamp}" + "&end_timestamp=" +
                                      f"{current_timestamp}")

    if fan_speed_response.status_code != 200:
        logger.error('get_fan_speed - Invalid request')
    else:
        fan_speed_response_data = fan_speed_response.json()
        logger.info(
            f"Total number of new fan speed record is: {len(fan_speed_response_data)}")
        new_stats['num_fan_speed'] = stats['num_fan_speed'] + len(fan_speed_response_data)

        max_fan_speed = stats['max_fan_speed']
        for item in fan_speed_response_data:
            max_fan_speed = max(max_fan_speed, item['fan_speed']['fan_speed'])
            # logger.debug(f'Fan speed event {item["trace_id"]} processed')
        new_stats['max_fan_speed'] = max_fan_speed

    add_stats = Stats(
        new_stats["num_shell_temp"],
        new_stats["num_core_temp"],
        new_stats["num_fan_speed"],
        new_stats["max_fan_speed"],
        new_stats["max_shell_temp"],
        new_stats["max_core_temp"],
        new_stats["last_updated"]
    )
    session.add(add_stats)
    session.commit()
    session.close()

    logger.debug(
        f'The new processed statistics is {new_stats}')
    logger.info("Periodic Processing Ends")
    return


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    check_data()
    init_scheduler()
    app.run(port=8100, use_reloader=False)
