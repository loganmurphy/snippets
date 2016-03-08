#!/usr/bin/python

import app
from models.group import Group
from models.user import User
from models.snippet import Snippet
from models.link_tables import *

from random_words import RandomWords

from datetime import date, timedelta
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
random.shuffle(codenames)
group_names = set(codenames[0:num_groups])
def make_group(codename):
  #codename = random.choice(codenames)
  group = Group.get_or_create(db.session, id=codename)
  return group

groups = [make_group(name) for name in group_names]
db.session.commit()

members_per_group = 10
subscribers_per_group = 10
subscribers_per_user = 10
snippets_per_user = 10

# TODO: make it so that we don't need all these crazy slow commits everywhere

def subscribe_to_group(user, group):
  GroupSubscription.get_or_create(db.session, user_id=user.id, group_id=group.id)
  db.session.commit()

def add_to_group(user, group):
  GroupMembership.get_or_create(db.session, user_id=user.id, group_id=group.id)
  db.session.commit()

def subscribe_to_user(from_user, to_user):
  UserSubscription.get_or_create(db.session, from_user_id=from_user.id, to_user_id=to_user.id)
  db.session.commit()

def make_snippet(user, days_back):
  num_lines = random.randint(2, 30)
  lines = ['- ' +' '.join(rw.random_words(count=random.randint(4, 50)))
    for l in range(0, num_lines)]
  text = '\n'.join(lines)
  d = date.today() - timedelta(days=days_back)
  snippet = Snippet(user_id=user.id, text=text, created_at=d)
  return snippet

rw = RandomWords()

for u in users:
  for i in range(0, subscribers_per_group):
    subscribe_to_group(u, random.choice(groups))
  for i in range(0, subscribers_per_user):
    subscribe_to_user(random.choice(users), u)
  for i in range(0, snippets_per_user):
    snippet = make_snippet(u, 7*i)
    db.session.add(snippet)

for g in groups:
  for i in range(0, members_per_group):
    add_to_group(random.choice(users), g)


db.session.commit()






