import os
import webapp2
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import urlfetch

import model
import database
import json
import config

def checkAuk(s):
	reqs = s.request.headers
	if "Auk-Secret" in reqs:
		return reqs["Auk-Secret"] == config.aukSecret
	return False

class ExecScript(webapp2.RequestHandler):
	def get(self, user, durl):
		dq = database.getUserData(user)
		author = user

		# User inexistant (Wrong url?)
		if not dq:
			self.error(404)
			return

		doc = database.getDocument(dq, durl)

		user = users.get_current_user()
		if not user:
			self.error(403)
			return
		
		iscreator = user.nickname() == dq.handler
		if users.is_current_user_admin():
			iscreator = True

		# Can't execute other people's scripts
		if not iscreator:
			self.error(404)
			return

		input_text = {}
		input_text['Auk-Secret'] = config.aukSecret
		scriptURL = "http://"+config.aukURL+"/api/exec/"+author+"/"+durl
		scriptResult = urlfetch.fetch(scriptURL,headers=input_text)

		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'text/plain'
		self.response.out.write (scriptResult.content)

class ViewDocument(webapp2.RequestHandler):
	def get(self, user, durl, page=None):
		if not checkAuk(self):
			return self.error(403)

		from google.appengine._internal.django.utils.safestring import mark_safe
		dq = database.getUserData(user)

		# User inexistant (Wrong url?)
		if not dq:
			return self.error(404)

		if not durl:
			durl = user

		doc = database.getDocument(dq, durl)
		data = {}
		data["docid"] = durl

		if not doc:
			return self.error(404)

		else:
			# Retrieve page
			if page is None or not page.strip():
				page = "home"
			else:
				page = page.replace(".","")
			pdata = database.getPage(doc,page)

			if not pdata:
				return self.error(404)
			else:
				data["title"] = pdata.name
				data["content"] = mark_safe(pdata.content)
				data["pageurl"] = durl + "." + page

		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'application/json'
		self.response.out.write (json.dumps(data))

class EditDocument(webapp2.RequestHandler):
	def post(self, user, durl, page=None):
		if not checkAuk(self):
			return self.error(403)
		data = {}
		import datetime
		dq = database.getUserData(user)

		if page is None or not page.strip():
			page = "home"
		else:
			page = page.replace(".","")

		# User inexistant (Wrong url?)
		if not dq:
			return self.error(405)

		doc = database.getDocument(dq, durl)

		if not doc:
			# The documents doesn't exists, let's create it!
			d = model.Document(key_name = durl, isfav = False, surl = durl, created = datetime.datetime.utcnow(), modified = datetime.datetime.utcnow(), views = 0, parent = dq)
			d.put()

			# If the document doesn't exist the page also doesn't
			p = model.Page(key_name = page, surl = page, name = self.request.get("title"), content = self.request.get("content"), parent = d)
			p.put()
		else:
			p = database.getPage(doc,page)

			if not p:
				# Page doesn't exist, let's make it!
				p = model.Page(key_name = page, surl = page, name = self.request.get("title"), content = self.request.get("content"), parent = doc)
			else:
				# Page already exists, just modify it..
				p.name = self.request.get("title")
				p.content = self.request.get("content")

			database.invalidatePage(doc, p.surl)
			p.put()
			doc.modified = datetime.datetime.utcnow()
			database.invalidateDocument(dq, doc.surl)
			doc.put()

		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.out.write ("done")

class PageList(webapp2.RequestHandler):
	def get(self, user, durl):
		if not checkAuk(self):
			return self.error(403)
		data = []
		from google.appengine._internal.django.utils.safestring import mark_safe

		dq = database.getUserData(user)

		# User inexistant (Wrong url?)
		if not dq:
			return self.error(404)

		doc = database.getDocument(dq, durl)

		ps = db.Query(model.Page)
		ps.ancestor(doc)

		for x in ps:
			data.append({"url":"../"+durl+"."+x.surl,"name":x.name if x.name != "" else "[Untitled Page]", "surl":x.surl})

		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'application/json'
		self.response.out.write (json.dumps(data))

class GetUser(webapp2.RequestHandler):
	def get(self):
		if not checkAuk(self):
			return self.error(403)
		data = {}
		# Get user status
		user = users.get_current_user()
		if user:
			data["handler"] = user.nickname()
			dq = database.getUserDataByHandler(user.nickname())
			if dq:
				data["name"] = dq.name
			else:
				return self.error(403)
		else:
			return self.error(403)
		
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'application/json'
		self.response.out.write (json.dumps(data))

class DocList(webapp2.RequestHandler):
	def get(self, what):
		if not checkAuk(self):
			return self.error(403)
		data = {}

		user = users.get_current_user()
		if not user:
			return self.error(403)
		
		# Get user
		dq = database.getUserDataByHandler(user.nickname())

		# User not registered
		if not dq:
			return self.error(403)
		
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

		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'application/json'
		self.response.out.write (json.dumps(data["dlist"]))