from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from base import Base

db = SQLAlchemy()

class Group(Base):
  __tablename__ = 'group'

  id = db.Column(db.String(50), unique=True, primary_key=True)