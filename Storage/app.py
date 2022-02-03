import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from fan_speed import FanSpeed
from temperature import Temperature

DB_ENGINE = create_engine("sqlite:///readings.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def report_temperature(body):
    """ Receives a hardware temperature """
    session = DB_SESSION()
    temp = Temperature(body['ming_rig_id'],
                       body['ming_card_id'],
                       body['timestamp'],
                       body['temperature']['ming_card_model'],
                       body['temperature']['core_temperature'],
                       body['temperature']['shell_temperature'])
    session.add(temp)
    session.commit()
    session.close()
    return NoContent, 201


def report_fan_speed(body):
    """ Receives a fan speed """
    session = DB_SESSION()
    fs = FanSpeed(body['ming_rig_id'],
                  body['ming_card_id'],
                  body['timestamp'],
                  body['fan_speed']['fan_speed'],
                  body['fan_speed']['fan_position'],
                  body['fan_speed']['ming_card_model'])
    session.add(fs)
    session.commit()
    session.close()
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090, debug=True)
