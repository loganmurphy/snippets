import os
import sys

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from models.base import Base

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'this is very secret'

db = SQLAlchemy(app)

engine = create_engine('sqlite:///dbdir/lite.db')

Base.metadata.create_all(engine)

