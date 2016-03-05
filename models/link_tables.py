from flask.ext.sqlalchemy import SQLAlchemy
from base import Base

db = SQLAlchemy()

class GroupSubscription(Base):
  __tablename__ = 'subscription'
  user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
  group_id = db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)

class GroupMembership(Base):
  __tablename__ = 'membership'
  user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
  group_id = db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)

# subscription = db.Table('subscription',
#   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#   db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
# )

# membership = db.Table('membership',
#   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#   db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
# )