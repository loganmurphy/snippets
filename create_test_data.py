#!/usr/bin/python

import app
from models.group import Group
from models.user import User
from models.link_tables import *

import random

db = app.db

test_data_dir = 'testdata'

first_names = [l.strip() for l in open(test_data_dir + '/first-names.txt')]
last_names = [l.strip() for l in open(test_data_dir + '/last-names.txt')]

codenames = [l.strip() for l in open(test_data_dir + '/codenames.txt')]

# create users
num_users = 1000
def make_user():
  first_name = random.choice(first_names)
  last_name = random.choice(last_names)
  email = '%s.%s@gmail.com' % (first_name, last_name)
  user = User.get_or_create(db.session,
    id=email,
    email=email,
    first_name=first_name,
    last_name=last_name,
    name='%s %s' % (first_name, last_name)
  )
  return user

users = [make_user() for i in range(0, num_users)]
db.session.commit()

# create groups
num_groups = 100
def make_group():
  codename = random.choice(codenames)
  group = Group.get_or_create(db.session, id=codename)
  return group

groups = [make_group() for i in range(0, num_groups)]
db.session.commit()

members_per_group = 10
subscribers_per_group = 10
subscribers_per_user = 10

def subscribe_to_group(user, group):
  GroupSubscription.get_or_create(db.session, user_id=user.id, group_id=group.id)

def add_to_group(user, group):
  GroupMembership.get_or_create(db.session, user_id=user.id, group_id=group.id)

def subscribe_to_user(from_user, to_user):
  UserSubscription.get_or_create(db.session, from_user_id=from_user.id, to_user_id=to_user.id)

for u in users:
  for i in range(0, subscribers_per_group):
    subscribe_to_group(u, random.choice(groups))
  for i in range(0, subscribers_per_user):
    subscribe_to_user(random.choice(users), u)

for g in groups:
  for i in range(0, members_per_group):
    add_to_group(random.choice(users), g)

db.session.commit()






