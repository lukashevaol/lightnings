from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import pytz

Base = declarative_base()


class Coordinate(Base):
    __tablename__ = 'coordinates'
    id = Column(Integer, primary_key=True)
    p1t = Column(String)
    p1n = Column(String)
    p2t = Column(String)
    p2n = Column(String)
    p3t = Column(String)
    p3n = Column(String)
    p4t = Column(String)
    p4n = Column(String)
    DS = Column(DateTime)
    DE = Column(DateTime)
    cnt = Column(String)
    u = datetime.utcnow()
    u = u.replace(tzinfo=pytz.utc)
    SaveDate = Column(DateTime, default=u)

    def __repr__(self):
        return "<Coordinate(id='{}', p1t='{}', SaveDate={})>" \
            .format(self.id, self.p1t, self.SaveDate)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    shortcode = Column(String)
    photo = Column(String)
    lat = Column(String)
    lng = Column(String)

    def __repr__(self):
        return "<Post(shortcode='{}', photo='{}', lat={}, lng={})>" \
            .format(self.shortcode, self.photo, self.lat, self.lng)
