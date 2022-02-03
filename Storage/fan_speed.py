from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class FanSpeed(Base):
    """ Fan Speed """

    __tablename__ = "fan_speed"

    id = Column(Integer, primary_key=True)
    ming_rig_id = Column(String(250), nullable=False)
    ming_card_id = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    fan_speed = Column(Integer, nullable=False)
    fan_position = Column(String(100), nullable=False)
    trace_id = Column(String(100), nullable=False)
    ming_card_model = Column(String(100), nullable=False)

    def __init__(self, trace_id, ming_rig_id, ming_card_id, timestamp, fan_speed, fan_position, ming_card_model):
        """ Initializes a fan speed reading """
        self.trace_id = trace_id
        self.ming_rig_id = ming_rig_id
        self.ming_card_id = ming_card_id
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.fan_speed = fan_speed
        self.fan_position = fan_position
        self.ming_card_model = ming_card_model


    def to_dict(self):
        """ Dictionary Representation of a fan speed reading """
        dict = {}
        dict['trace_id'] = self.trace_id
        dict['ming_rig_id'] = self.ming_rig_id
        dict['ming_card_id'] = self.ming_card_id
        dict['fan_speed'] = {}
        dict['fan_speed']['fan_speed'] = self.fan_speed
        dict['fan_speed']['fan_position'] = self.fan_position
        dict['fan_speed']['ming_card_model'] = self.ming_card_model
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
