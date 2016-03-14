from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base, get_or_create

db = SQLAlchemy()

class Snippet(Base):
  __tablename__ = 'snippets'
  id = db.Column(db.Integer, unique=True, primary_key=True)
  user_id = db.Column('user_id', db.String, db.ForeignKey('user.id'))
  created_at = db.Column('created_at', db.DateTime)
  text = db.Column('text', db.Text)
  recipient = db.Column('recipient', db.String)
  html = db.Column('html', db.Text, nullable=True)

  def __init__(self, user_id, text, recipient, html, created_at=None):
    self.user_id = user_id
    self.text = text
    self.recipient = recipient
    self.html = html
    self.created_at = created_at or datetime.now()
