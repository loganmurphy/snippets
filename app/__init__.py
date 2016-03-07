import os
import sys

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models.base import Base

from models.group import Group
from models.user import User
from models.link_tables import *

app = Flask(__name__)
Bootstrap(app)

app.config.from_object('config.DevelopmentConfig')
app.secret_key = app.config['SECRET_KEY']

engine = create_engine(app.config['DATABASE_URI'])

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base.metadata.create_all(engine)
db_session.commit()

Base.query = db_session.query_property()

class Database():
  def __init__(self, session):
    self.session = session

db = Database(db_session)
