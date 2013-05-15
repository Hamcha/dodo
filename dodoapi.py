import os
import webapp2
from google.appengine.ext import db
from google.appengine.api import users

import model
import database
import json

class ViewDocument(webapp2.RequestHandler):

	def get(self, user, durl, page):
		from google.appengine._internal.django.utils.safestring import mark_safe

		dq = database.getUserData(user)

		# User inexistant (Wrong url?)
		if not dq:
			self.error(404)
			return

		if not durl:
			durl = user

		doc = database.getDocument(dq, durl)

		data = {}
		data["docid"] = durl

		if not doc:
			self.error(404)
		else:
			# Retrieve page
			if page is None or not page.strip():
				page = "home"
			else:
				page = page.replace(".","")

			pdata = database.getPage(doc,page)

			if not pdata:
				self.error(404)
			else:
				data["title"] = pdata.name
				data["content"] = mark_safe(pdata.content)
				data["pageurl"] = durl + "." + page

		self.response.headers ['Content-Type'] = 'application/json'
		self.response.out.write (json.dumps(data))

class GetUser(webapp2.RequestHandler):
	def get(self):
		data = {}
		# Get user status
		user = users.get_current_user()
		if user:
			data["handler"] = user.nickname()
			dq = database.getUserDataByHandler(user.nickname())
			if dq:
				data["name"] = dq.name
			else:
				self.error(403)
				return
		else:
			self.error(403)
			return
		
		self.response.headers ['Content-Type'] = 'application/json'
		self.response.out.write (json.dumps(data))

class DocList(webapp2.RequestHandler):
	def get(self, what):
		data = {}

		user = users.get_current_user()
		if not user:
			self.error(403)
			return

		# Get user
		dq = database.getUserDataByHandler(user.nickname())


		# User not registered
		if not dq:
			self.error(403)
			return

		# Get document (if it exists)
		query = db.Query(model.Document)
		query.ancestor(dq)
		if what == "/pinned":
			query.filter("isfav =", True)
		data["dlist"] = []
		for p in query:
			page = database.getPage(p,"home")
			x = {}
			x["url"] = dq.name + "/" + p.surl
			x["name"] = page.name
			data["dlist"].append(x)

		self.response.headers ['Content-Type'] = 'application/json'
		self.response.out.write (json.dumps(data["dlist"]))