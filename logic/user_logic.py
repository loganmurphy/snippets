from app import db
from models.group import Group
from models.user import User
from models.snippet import Snippet
from models.link_tables import *

from datetime import date, datetime, timedelta

class UserLogic():
  @staticmethod
  def find_user_by_email(email):
    return db.session.query(User).filter_by(id=email).one()

  @staticmethod
  def subscribe_to_user(from_user, to_user):
    sub = UserSubscription.get_or_create(
      db.session,
      from_user_id = from_user.id,
      to_user_id = to_user.id
    )
    db.session.commit()
    return sub

  @staticmethod
  def unsubscribe_to_user(from_user, to_user):
    db.session.query(UserSubscription).filter_by(
      from_user_id = from_user.id,
      to_user_id = to_user.id
    ).delete()
    db.session.commit()

  @staticmethod 
  def get_last_snippets(user, max_weeks=10):
    d = date.today() - timedelta(days=max_weeks+1)
    return db.session.query(Snippet).filter(
      Snippet.created_at >= d,
      Snippet.user_id == user.id
    ).order_by(Snippet.created_at.desc())