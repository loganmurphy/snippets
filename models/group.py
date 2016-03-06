from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base, get_or_create

db = SQLAlchemy()

class Group(Base):
  __tablename__ = 'group'
  id = db.Column(db.String(50), unique=True, primary_key=True)

  def __init__(self, id):
    self.id = id