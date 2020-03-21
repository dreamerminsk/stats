from urllib.parse import urlparse, parse_qsl

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Forum(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    @classmethod
    def parse(cls, html):
        query = urlparse(html.get("href")).query
        params = dict(parse_qsl(query))
        c = Forum(id=params["c"], name=html.text)
        return c

    def __repr__(self):
        return "<Forum(id='%s', name='%s')>" % (self.id, self.name)


class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    likes = Column(Integer)

    def __repr__(self):
        return "<Topic(id='%s', name='%s', likes='%d')>" % (self.id, self.name, self.likes)
