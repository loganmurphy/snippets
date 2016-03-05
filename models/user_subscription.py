from flask_sqlalchemy import SQLAlchemy
from app import db

class UserSubscription(db.Model):
  __tablename__ = 'user_subscription'

  id = db.Column(db.Integer, primary_key=True)
  from_user = db.Column(db.String(500))
  to_user = db.Column(db.String(500))
