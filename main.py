from flask import Flask
from flask import render_template
from flask import abort, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager

from auth import OAuthSignIn

from models.user import User
from models.group import Group

from app import app, db

import pdb

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
  try:
    return db.session.query(User).filter_by(id=id).one()
  except:
    return None

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
  # Flask-Login function
  if not current_user.is_anonymous:
    return redirect(url_for('index'))
  oauth = OAuthSignIn.get_provider(provider)
  return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
  if not current_user.is_anonymous:
    return redirect(url_for('index'))
  oauth = OAuthSignIn.get_provider(provider)
  me_dict = oauth.callback()
  email = me_dict['email']

  if email is None:
    # I need a valid email address for my user identification
    flash('Authentication failed.')
    return redirect(url_for('index'))

  # Look if the user already exists
  user = User.get_or_create(db.session, id=email)
  user.first_name = me_dict['given_name']
  user.family_name = me_dict['family_name']
  user.email = me_dict['email']
  user.picture = me_dict['picture']
  user.name = me_dict['name']
  db.session.commit()

  # Log in the user, by default remembering them for their next visit
  # unless they log out.
  login_user(user, remember=True)
  return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user is not None and current_user.is_authenticated:
    return redirect(url_for('index'))
  return render_template('login.html')

@app.route('/')
@login_required
def index():
  return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return render_template('index.html')

@app.route('/groups')
@login_required
def groups():
  groups = db.session.query(Group).order_by(Group.id)
  return render_template('groups.html',
    groups=groups
  )

@app.route('/groups/<name>')
@login_required
def group_detail(name):
  group = db.session.query(Group).filter_by(id=name).one()
  return render_template('group_detail.html',
    group=group
  )


@app.route('/users/<email>')
@login_required
def user_detail(email):
  user = db.session.query(User).filter_by(id=email).one()
  return render_template('user_detail.html',
    user=user
  )


### NAV

from flask_nav import Nav
from flask_nav.elements import Navbar, View

nav = Nav()

@nav.navigation()
def mynavbar():
  return Navbar(
    'mysite',
    View('Home', 'index'),
  )
# ...

nav.init_app(app)

### 

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
