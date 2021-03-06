from flask.ext.sqlalchemy import SQLAlchemy
from base import Base
from sqlalchemy.orm import relationship

dummyDB = SQLAlchemy()

class GroupSubscription(Base):
  __tablename__ = 'group_subscription'
  user_id = dummyDB.Column('user_id', dummyDB.String, dummyDB.ForeignKey('user.id'), primary_key=True)
  group_id = dummyDB.Column('group_id', dummyDB.String, dummyDB.ForeignKey('group.id'), primary_key=True)

  group = relationship('Group', back_populates='subscribers')
  user = relationship('User', back_populates='group_subscriptions')

  def __init__(self, user_id, group_id):
    self.user_id = user_id
    self.group_id = group_id

class GroupMembership(Base):
  __tablename__ = 'group_membership'
  user_id = dummyDB.Column('user_id', dummyDB.String, dummyDB.ForeignKey('user.id'), primary_key=True)
  group_id = dummyDB.Column('group_id', dummyDB.String, dummyDB.ForeignKey('group.id'), primary_key=True)

  group = relationship('Group', back_populates='members')
  user = relationship('User', back_populates='group_memberships')

  def __init__(self, user_id, group_id):
    self.user_id = user_id
    self.group_id = group_id

class UserSubscription(Base):
  __tablename__ = 'user_subscription'
  from_user_id = dummyDB.Column('from_user_id', dummyDB.String, dummyDB.ForeignKey('user.id'), primary_key=True)
  to_user_id = dummyDB.Column('to_user_id', dummyDB.String, dummyDB.ForeignKey('user.id'), primary_key=True)

  from_user = relationship('User', back_populates='users_following', foreign_keys=[from_user_id])
  to_user = relationship('User', back_populates='users_followees', foreign_keys=[to_user_id])

  def __init__(self, from_user_id, to_user_id):
    self.from_user_id = from_user_id
    self.to_user_id = to_user_id