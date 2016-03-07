from app import db
from models.group import Group
from models.user import User
from models.link_tables import *

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
