from google.appengine.ext import db

class User(db.Model):
	name = db.StringProperty()
	handler = db.StringProperty()

class Document(db.Model):
	surl = db.StringProperty()
	created = db.DateTimeProperty()
	modified = db.DateTimeProperty()
	views = db.IntegerProperty()
	isfav = db.BooleanProperty()

class Page(db.Model):
	surl = db.StringProperty()
	name = db.StringProperty()
	content = db.TextProperty()