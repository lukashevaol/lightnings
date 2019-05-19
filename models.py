from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import pytz

Base = declarative_base()
u = datetime.utcnow()
u = u.replace(tzinfo=pytz.utc)


class Coordinate(Base):
    '''
    Contains lightnings info: area, time, number of lightnings
    '''
    __tablename__ = 'coordinates'
    id = Column(Integer, primary_key=True)
    first_point_lat = Column(String)
    first_point_lng = Column(String)
    second_point_lat = Column(String)
    second_point_lng = Column(String)
    third_point_lat = Column(String)
    third_point_lng = Column(String)
    fourth_point_lat = Column(String)
    fourth_point_lng = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    count = Column(String)
    save_date = Column(DateTime, default=u)

    def __repr__(self):
        return "<Coordinate(id='{}', SaveDate={})>" \
            .format(self.id, self.save_date)


class Post(Base):
    '''
    Contains post info: shortcode, photo link, coordinates
    '''
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    shortcode = Column(String)
    photo = Column(String)
    lat = Column(String)
    lng = Column(String)

    def __repr__(self):
        return "<Post(shortcode='{}', photo='{}', lat={}, lng={})>" \
            .format(self.shortcode, self.photo, self.lat, self.lng)
