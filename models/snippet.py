from flask_sqlalchemy import SQLAlchemy
from app import db

class Snippet(db.Model):
  __tablename__ = 'snippet'

  id = db.Column(db.Integer, primary_key=True)
  user = db.Column(db.String(500))
  created_at = db.Column(db.DateTime)
  week = db.Column(db.Integer)
  year = db.Column(db.Integer)