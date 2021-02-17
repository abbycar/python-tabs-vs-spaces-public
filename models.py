from sqlalchemy import Column, Integer, String, DateTime
from flask import Flask

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Votes(Base):
    __tablename__ = 'votes'
    vote_id = Column(Integer, primary_key=True)
    time_cast = Column(DateTime)
    candidate = Column(String(6))


def create_database(engine):
    """
    Create tables stored in meta to database
    """
    app = Flask(__name__)
    with app.app_context():
        Base.metadata.create_all(engine)
    print("All tables created")