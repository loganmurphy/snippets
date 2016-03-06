from flask.ext.sqlalchemy import SQLAlchemy
from base import Base

db = SQLAlchemy()

class GroupSubscription(Base):
  __tablename__ = 'group_subscription'
  user_id = db.Column('user_id', db.String, db.ForeignKey('user.id'), primary_key=True)
  group_id = db.Column('group_id', db.String, db.ForeignKey('group.id'), primary_key=True)

  def __init__(self, user_id, group_id):
    self.user_id = user_id
    self.group_id = group_id

class GroupMembership(Base):
  __tablename__ = 'group_membership'
  user_id = db.Column('user_id', db.String, db.ForeignKey('user.id'), primary_key=True)
  group_id = db.Column('group_id', db.String, db.ForeignKey('group.id'), primary_key=True)

  def __init__(self, user_id, group_id):
    self.user_id = user_id
    self.group_id = group_id

class UserSubscription(Base):
  __tablename__ = 'user_subscription'
  from_user_id = db.Column('from_user_id', db.String, db.ForeignKey('user.id'), primary_key=True)
  to_user_id = db.Column('to_user_id', db.String, db.ForeignKey('user.id'), primary_key=True)

  def __init__(self, from_user_id, to_user_id):
    self.from_user_id = from_user_id
    self.to_user_id = to_user_id