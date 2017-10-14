"""
    Classes that describe tables
"""
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from sqlalchemy import Column, DateTime, Integer, Numeric, String, ForeignKey
from sqlalchemy import Sequence

# create the base class of all ORM classes
Base = declarative_base()

class Metric(Base):
    __tablename__ = "metrics"

    id = Column('id', Integer, Sequence('metric_seq'), primary_key=True, nullable=False)
    name = Column('name', String, nullable=False)
    unit = Column('unit', String, nullable=False)
    description = Column('description', String, nullable=True)
    created_at = Column('created_at', DateTime, server_default=text('NOW()'))
    updated_at = Column('update_at', DateTime, server_default=text('NOW()'))

    def __repr__(self):
        return "Metric: name={}, unit={}, description={}".\
        format(self.name, self.unit, self.description)

class Station(Base):
    __tablename__ = "station_data"

    id = Column('id', Integer, Sequence('station_seq'), primary_key=True, nullable=False)
    net = Column('net', String, nullable=False)
    sta = Column('sta', String, nullable=False)
    ondate = Column('ondate', DateTime, nullable=False)
    offdate = Column('offdate', DateTime, default=datetime.datetime(3000,1,1))
    lat = Column('lat', Numeric)
    lon = Column('lon', Numeric)
    elev = Column('elev', Numeric)
    channels = Column('channels',Integer[])
    created_at = Column('created_at', DateTime, server_default=text('NOW()'))
    updated_at = Column('created_at', DateTime, server_default=text('NOW()'))

    def __repr__(self):
        return "Station: net={}, sta={}, ondate={}, lat={}, lon={}, elev={}, #channels={}".\
        format(self.net,self.sta,self.ondate.isoformat(),self.lat,self.lon,self.elev, len(self.channels))

class Channel(Base):
    __tablename__ = "channels"

    id = Column('id', Integer, Sequence('chan_seq'), primary_key=True, nullable=False)
    net = Column('net', String(8), nullable=False)
    sta = Column('sta', String(6), nullable=False)
    seedchan = Column('seedchan', String(3), nullable=False)
    location = Column('location', String(2), nullable=False)
    ondate = Column('ondate', DateTime, nullable=False)
    lat = Column('lat', Double)
    lon = Column('lon', Double)
    elev = Column('elev', Double)
    edepth = Column('edepth', Double)
    azimuth = Column('azimuth', Double)
    dip = Column('dip', Double)
    samprate = Column('samprate', Double, nullable=False)
    offdate = Column('offdate', DateTime, default=datetime.datetime(3000,1,1))
    created_at = Column('create_at', DateTime, server_default=text('NOW()'))

    def __repr__(self):
        return "Channel: net={}, sta={}, seedchan={}, location={}, ondate={}, offdate={}".\
        format(self.net, self.sta, self.seedchan, self.location, self.ondate, self.offdate)
