from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from base import Base

from models import link_tables

db = SQLAlchemy()

class User(Base):
  __tablename__ = 'user'
  id = db.Column(db.String(500), unique=True, primary_key=True)

  subscriptions = db.relationship(
      'Group', 
      secondary='subscription',
      backref=db.backref('subscribers', lazy='dynamic')
    )

  subscriptions = db.relationship(
      'Group', 
      secondary='membership',
      backref=db.backref('subscribers', lazy='dynamic')
    )

  def __init__(self, email):
    self.email = email

  def get_username(self):
    return self.email

  def get_id(self):
    return self.email

  @property  
  def is_active(self):
    return True

  @property
  def is_authenticated(self):
    return True

  @staticmethod
  def find_or_create_by_email(email):
    return User(email)

  @staticmethod
  def find_by_id(id):
    return User(id)

# this is what it might look like if we were a real application
# user=User.query.filter_by(email=email).first()
# if not user:
#     # Create the user. Try and use their name returned by Google,
#     # but if it is not set, split the email address at the @.
#     nickname = username
#     if nickname is None or nickname == "":
#         nickname = email.split('@')[0]

#     # We can do more work here to ensure a unique nickname, if you 
#     # require that.
#     user=User(nickname=nickname, email=email)
#     db.session.add(user)
#     db.session.commit()