from app import db
from models.group import Group
from models.user import User
from models.link_tables import *

class GroupLogic():
  @staticmethod
  def find_group_by_name(name):
    return db.session.query(Group).filter_by(id=name).one()

  @staticmethod
  def find_all_groups():
    return db.session.query(Group).order_by(Group.id)

  @staticmethod
  def subscribe_to_group(user, group):
    GroupSubscription.get_or_create(
      db.session,
      user_id = user.id,
      group_id = group.id
    )
    db.session.commit()

  @staticmethod
  def unsubscribe_to_group(user, group):
    db.session.query(GroupSubscription).filter_by(
      user_id = user.id,
      group_id = group.id
    ).delete()
    db.session.commit()

  @staticmethod
  def get_users_in_group(group):
    return GroupMembership.query.filter_by(group=group.name)


