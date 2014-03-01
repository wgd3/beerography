from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class Beer(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100), unique = True)
	brewery = db.Column(db.String(100))
	style = db.Column(db.String(100))
