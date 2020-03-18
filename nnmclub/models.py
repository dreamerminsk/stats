from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    @classmethod
    def parse(cls, html):
        c = Category(id=1, name=html.text)
        return c

    def __repr__(self):
        return "<Category(id='%s', name='%s')>" % (self.id, self.name)
