from sqlalchemy import Column, Integer, DateTime

from base import Base


class Stats(Base):
    """ processing Statistics """
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    num_core_temp = Column(Integer, nullable=False)
    num_shell_temp = Column(Integer, nullable=False)
    num_fan_speed = Column(Integer, nullable=False)
    avg_core_temp = Column(Integer, nullable=True)
    avg_shell_temp = Column(Integer, nullable=True)
    avg_fan_speed = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_core_temp, num_shell_temp, avg_shell_temp,
                 avg_core_temp, num_fan_speed, avg_fan_speed,
                 last_updated):
        """ Initializes a processing statistics objet """
        self.num_core_temp = num_core_temp
        self.num_shell_temp = num_shell_temp
        self.num_fan_speed = num_fan_speed
        self.avg_core_temp = avg_core_temp
        self.avg_shell_temp = avg_shell_temp
        self.avg_fan_speed = avg_fan_speed
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_core_temp'] = self.num_core_temp
        dict['num_shell_temp'] = self.num_shell_temp
        dict['num_fan_speed'] = self.num_fan_speed
        dict['avg_core_temp'] = self.avg_core_temp
        dict['avg_shell_temp'] = self.avg_shell_temp
        dict['avg_fan_speed'] = self.avg_fan_speed
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        return dict
