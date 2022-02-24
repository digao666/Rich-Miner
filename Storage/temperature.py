from sqlalchemy import Column, Integer, String, DateTime

from base import Base


class Temperature(Base):
    """ Temperature """

    __tablename__ = "temperature"

    id = Column(Integer, primary_key=True)
    ming_rig_id = Column(String(250), nullable=False)
    ming_card_id = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    core_temperature = Column(Integer, nullable=False)
    shell_temperature = Column(Integer, nullable=False)
    trace_id = Column(String(100), nullable=False)

    def __init__(self, trace_id, date_created, ming_rig_id, ming_card_id, timestamp, core_temperature,
                 shell_temperature):
        """ Initializes a temperature reading """
        self.trace_id = trace_id
        self.ming_rig_id = ming_rig_id
        self.ming_card_id = ming_card_id
        self.timestamp = timestamp
        self.date_created = date_created
        self.core_temperature = core_temperature
        self.shell_temperature = shell_temperature

    def to_dict(self):
        """ Dictionary Representation of a temperature reading """
        dict = {}
        dict['trace_id'] = self.trace_id
        dict['ming_rig_id'] = self.ming_rig_id
        dict['ming_card_id'] = self.ming_card_id
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['temperature'] = {}
        dict['temperature']['core_temperature'] = self.core_temperature
        dict['temperature']['shell_temperature'] = self.shell_temperature

        return dict
