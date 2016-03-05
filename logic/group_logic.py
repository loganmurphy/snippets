from models.group_membership import GroupMembership
from models.group_subscription import GroupSubscription
from app import db

class GroupLogic():
  @staticmethod
  def subscribe_to_group(user, group):
    db.session.add(
      GroupSubscription(
        username = user.get_username(),
        groupname = group.name
      )
    )
    db.session.commit()

  @staticmethod
  def get_users_in_group(group):
    return GroupMembership.query.filter_by(group=group.name)


    