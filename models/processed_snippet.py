from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base, get_or_create

db = SQLAlchemy()

"""
This table is used to "reserve" processing of a message by UID.  The email processor writes into this table
transactionally before performing IMAP operations on the message (like moving or deleting it).  This allows multiple
instances of the app to coordinate through the DB.
"""
class ProcessedSnippet(Base):
  __tablename__ = 'processed_snippets'
  msg_uid = db.Column(db.String, unique=True, primary_key=True)
  user_id = db.Column('user_id', db.String, db.ForeignKey('user.id'))
  processed_at = db.Column('created_at', db.DateTime)
  recipient = db.Column('recipient', db.String)

  def __init__(self, msg_uid, user_id, recipient):
    self.msg_uid = msg_uid
    self.user_id = user_id
    self.recipient = recipient
    self.processed_at = datetime.now()
