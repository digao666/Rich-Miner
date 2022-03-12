import connexion
import datetime
import logging.config
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS
from base import Base
from stats import Stats

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
mysql_db_url = app_config['eventstore']['url']

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('processing')

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_stats():
    """ Gets the temperature and fan speed events stats  """
    session = DB_SESSION()
    logger.info("Start Get Stats request")
    readings = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    result = readings.to_dict()
    if not result:
        logger.debug(f'No latest statistics found')
        return "Statistics do not exist", 404
    logger.debug(f'The latest statistics is {result}')
    logger.info("Get Stats request done")
    session.close()
    return result, 200


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic processing")
    session = DB_SESSION()
    reading = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if not reading:
        result = {
            "num_core_temp": 0,
            "num_shell_temp": 0,
            "avg_shell_temp": 0,
            "avg_core_temp": 0,
            "num_fan_speed": 0,
            "avg_fan_speed": 0,
            "last_updated": datetime.datetime.now()
        }
    result = reading.to_dict()
    timestamp = result['last_updated'].strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {'timestamp': timestamp}

    # Temperature
    get_temperature = f'{mysql_db_url}/status/temperature?timestamp={timestamp}'
    temperature_response = requests.get(get_temperature, params=params)

    if temperature_response.status_code != 200:
        logger.error('get_temperature - Invalid request')
    else:
        temperature_response_data = temperature_response.json()
        logger.info(
            f"Total number of new temperatures is: {len(temperature_response_data)}")

        new_stats['num_core_temp'] = len(temperature_response_data)
        new_stats['num_shell_temp'] = len(temperature_response_data)

        total_shell_temp = 0
        total_core_temp = 0
        for item in temperature_response_data:
            total_shell_temp = total_shell_temp + item['temperature']['shell_temperature']
            total_core_temp = total_core_temp + item['temperature']['core_temperature']
            # logger.debug(f'Temperature event {item["trace_id"]} processed')
        if len(temperature_response_data) != 0:
            avg_shell_temp = round(total_shell_temp / len(temperature_response_data), 2)
        else:
            avg_shell_temp = 0

        if len(temperature_response_data) != 0:
            avg_core_temp = round(total_shell_temp / len(temperature_response_data), 2)
        else:
            avg_core_temp = 0
        new_stats['avg_shell_temp'] = avg_shell_temp
        new_stats['avg_core_temp'] = avg_core_temp

    # fan speed
    get_fan_speed = f'{mysql_db_url}/status/fanspeed?timestamp={timestamp}'
    fan_speed_response = requests.get(get_fan_speed, params=params)

    if fan_speed_response.status_code != 200:
        logger.error('get_fan_speed - Invalid request')
    else:
        fan_speed_response_data = fan_speed_response.json()
        logger.info(
            f"Total number of new fan speed record is: {len(fan_speed_response_data)}")
        new_stats['num_fan_speed'] = len(fan_speed_response_data)

        total_fan_speed = 0
        for item in fan_speed_response_data:
            total_fan_speed = total_fan_speed + item['fan_speed']['fan_speed']
            # logger.debug(f'Fan speed event {item["trace_id"]} processed')
        if len(fan_speed_response_data) != 0:
            avg_fan_speed = round(total_fan_speed / len(fan_speed_response_data), 2)
        else:
            avg_fan_speed = 0
        new_stats['avg_fan_speed'] = avg_fan_speed

    add_stats = Stats(new_stats["num_core_temp"], new_stats["num_shell_temp"], new_stats["avg_shell_temp"],
                      new_stats["avg_core_temp"], new_stats["num_fan_speed"], new_stats["avg_fan_speed"],
                      new_stats["last_updated"]
                      )
    session.add(add_stats)
    session.commit()
    session.close()

    logger.debug(f'The new processed statistics is {new_stats}')
    logger.info("Periodic processing Ends")
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
    init_scheduler()
    app.run(port=8100, use_reloader=False)
