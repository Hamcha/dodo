import os
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users

import model
import database

experimental = True

# Set landing page
# Example: /user/doc.page is ["user", "doc", "page"]
# Set to None to land on the Login Page (like previous versions of dodo)
homepage = ["hamcha", "dodo", "landing"]

class ViewDocument(webapp2.RequestHandler):

	def get(self, user, durl = None, page = None):
		from google.appengine._internal.django.utils.safestring import mark_safe

		data = {}
		data = enrich(data)

		dq = database.getUserData(user)

		# User inexistant (Wrong url?)
		if not dq:
			self.error(404)
			return

		if not durl:
			durl = user

		doc = database.getDocument(dq, durl)

		user = users.get_current_user()
		data["durl"] = durl
		data["iscreator"] = False if not user else user.nickname() == dq.handler
		if users.is_current_user_admin():
			data["iscreator"] = True

		if not doc:
			if not data["iscreator"]:
				self.error(404)
				return
			data["iserror"] = True
			data["title"] = mark_safe("This document doesn't exist <span style=\"color: #aaa;\">(yet?)</span>")
			data["content"] = mark_safe("<p>You have hit a document that doesn't exist, want to <a href=\""+ durl +"/edit\">create it</a>?</p>")
		else:
			# Retrieve page
			if page is None or not page.strip():
				page = "home"
			else:
				page = page.replace(".","")

			data["ispinned"] = doc.isfav

			pdata = database.getPage(doc,page)

			if not pdata:
				# Inexistant Page?
				data["iserror"] = True
				data["title"] = mark_safe("This page doesn't exist <span style=\"color: #aaa;\">(yet?)</span>")
				data["content"] = mark_safe("<p>You have hit a page that doesn't exist, want to <a href=\""+ durl + "." + page +"/edit\">create it</a>?</p>")
			else:
				data["title"] = pdata.name
				data["content"] = mark_safe(pdata.content)
				data["pageurl"] = durl + "." + page

		# Render template
		path = os.path.join (os.path.dirname (__file__), "template", "document.html")
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'text/html'
		self.response.out.write (template.render (path, data))

class EditDocument(webapp2.RequestHandler):
	def get(self, user, durl, page = None):
		from google.appengine._internal.django.utils.safestring import mark_safe

		data = {}
		data = enrich(data)

		dq = database.getUserData(user)

		# User inexistant (Wrong url?)
		if not dq:
			self.error(404)
			return

		doc = database.getDocument(dq, durl)

		user = users.get_current_user()
		data["iscreator"] = user.nickname() == dq.handler
		if users.is_current_user_admin():
			data["iscreator"] = True

		# Can't edit other people's document
		if not data["iscreator"]:
			self.error(404)
			return

		if doc == None:
			# Inexistant Document?
			data["title"] = ""
			data["content"] = mark_safe("Put your content here")
		else:
			# Retrieve page
			if page is None or not page.strip():
				page = "home"
			else:
				page = page.replace(".","")
			pdata = database.getPage(doc,page)
			if not pdata:
				# Inexistant Page?
				data["title"] = ""
				data["content"] = mark_safe("Put your content here")
			else:
				data["title"] = pdata.name
				data["content"] = pdata.content

		# Render template
		path = os.path.join (os.path.dirname (__file__), "template", "editor.html")
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'text/html'
		self.response.out.write (template.render (path, data))

	def post(self, user, durl, page = None):
		import datetime
		dq = database.getUserData(user)

		if page is None or not page.strip():
			page = "home"
		else:
			page = page.replace(".","")

		# User inexistant (Wrong url?)
		if not dq:
			self.error(405)
			return

		user = users.get_current_user()

		# Can't edit other people's document
		if (user.nickname() != dq.handler) and (users.is_current_user_admin() == False):
			self.error(405)
			return

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

		self.response.out.write ("done")

class DeleteDocument(webapp2.RequestHandler):
	def get(self, user, durl, page):

		dq = database.getUserData(user)

		data = {}
		data = enrich(data)

		# User inexistant (Wrong url?)
		if not dq:
			self.error(404)
			return

		user = users.get_current_user()
		data["iscreator"] = user.nickname() == dq.handler
		if users.is_current_user_admin():
			data["iscreator"] = True

		# Can't edit other people's document
		if not data["iscreator"]:
			self.error(403)
			return

		doc = database.getDocument(dq, durl)

		if not doc:
			self.error(404)
			return
		else:
			# Retrieve page
			if page is None or not page.strip():
				page = "home"
			else:
				page = page.replace(".","")
			data["issinglepage"] = (page != "home")
			data["name"] = doc.surl
			pdata = database.getPage(doc,page)
			if not pdata:
				self.error(404)
				return
			else:
				data["page"] = pdata.surl
				data["pname"] = pdata.name if pdata.name != "" else "[Untitled Page]"
				data["user"] = dq.name

		# Render template
		path = os.path.join (os.path.dirname (__file__), "template", "delete.html")
		self.response.headers ['Content-Type'] = 'text/html'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.out.write (template.render (path, data))

	def post(self, user, durl, page):
		
		dq = database.getUserData(user)

		if page is None or not page.strip():
			page = "home"
		else:
			page = page.replace(".","")

		# User inexistant (Wrong url?)
		if not dq:
			self.error(405)
			return

		user = users.get_current_user()

		# Can't delete other people's document
		if (user.nickname() != dq.handler) and (users.is_current_user_admin() == False):
			self.error(405)
			return

		doc = database.getDocument(dq, durl)

		if not doc:
			self.error(405)
			return
		else:
			if page == "home":
				# Delete the document and every page associated with it
				query = db.Query(model.Page)
				query.ancestor(doc)
				for x in query:
					database.invalidatePage(doc, x.surl)
					x.delete()

				database.invalidateDocument(dq, doc.surl)
				doc.delete()
			else:
				# Delete only the page
				p = database.getPage(doc,page)
				database.invalidatePage(doc, p.surl)
				p.delete()

		self.response.out.write ("done")

class LoginPage(webapp2.RequestHandler):
	def get(self):
		
		data = {}
		data = enrich(data)
		data["denied"] = True
		# Get user status
		user = users.get_current_user()
		if user:
			data["islogged"] = True
			data["name"] = user.nickname()
			data["url"] = users.create_logout_url("/home")
			dq = database.getUserDataByHandler(user.nickname())
			if dq:
				data["denied"] = False
				data["name"] = dq.name
				# Last created docs
				data["lastc"] = []
				lastc = db.Query(model.Document, keys_only=True)
				lastc.ancestor(dq)
				lastc.order("-created")
				for k in lastc.run(limit=8):
					p = database.getDocument(dq, k.name())
					page = database.getPage(p,"home")
					p.url = dq.name + "/" + p.surl
					p.name = page.name if page.name != "" else "[Untitled Page]"
					data["lastc"].append(p)
				# Last modified docs
				data["lastm"] = []
				lastm = db.Query(model.Document, keys_only=True)
				lastm.ancestor(dq)
				lastm.order("-modified")
				for k in lastm.run(limit=8):
					p = database.getDocument(dq, k.name())
					page = database.getPage(p,"home")
					p.url = dq.name + "/" + p.surl
					p.name = page.name if page.name != "" else "[Untitled Page]"
					data["lastm"].append(p)
				# 10 Favorite list
				data["lastfav"] = []
				favl = db.Query(model.Document, keys_only=True)
				favl.ancestor(dq)
				favl.filter("isfav =", True)
				favn = 0
				for k in favl.run(limit=7):
					p = database.getDocument(dq, k.name())
					page = database.getPage(p,"home")
					p.url = dq.name + "/" + p.surl
					p.name = page.name if page.name != "" else "[Untitled Page]"
					data["lastfav"].append(p)
					favn += 1
				if favn == 7:
					p = { "name": "See all pinned", "url":"list/pinned" }
					data["lastfav"].append(p)
		else:
			data["islogged"] = False
			data["url"] = users.create_login_url("/")
		# Render template
		path = os.path.join (os.path.dirname (__file__), "template", "home.html")
		
		self.response.headers ['Content-Type'] = 'text/html'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.out.write (template.render (path, data))

class HomePage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			# Get user
			dq = database.getUserDataByHandler(user.nickname())

			# User not registered
			if dq or homepage is None:
				self.redirect_to("login")
				return
		from google.appengine._internal.django.utils.safestring import mark_safe

		data = {}
		data = enrich(data)
		data["durl"] = homepage[1]

		dq = database.getUserData(homepage[0])
		doc = database.getDocument(dq, data["durl"])

		page = homepage[2]

		# Retrieve page
		if page is None or not page.strip():
			page = "home"
		else:
			page = page.replace(".","")

		data["ispinned"] = doc.isfav

		pdata = database.getPage(doc,page)

		data["title"] = pdata.name
		data["content"] = mark_safe(pdata.content)
		data["pageurl"] = homepage[1] + "." + page

		# Render template
		path = os.path.join (os.path.dirname (__file__), "template", "document.html")
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'text/html'
		self.response.out.write (template.render (path, data))




class DocList(webapp2.RequestHandler):
	def get(self, what):
		data = {}
		data = enrich(data)

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

		data["title"] = "List of all your documents"

		# Get document (if it exists)
		query = db.Query(model.Document)
		query.ancestor(dq)
		if what == "/pinned":
			query.filter("isfav =", True)
			data["title"] = "List of all your pinned documents"
		data["dlist"] = []
		for p in query:
			page = database.getPage(p,"home")
			p.url = dq.name + "/" + p.surl
			p.name = page.name if page.name != "" else "[Untitled Page]"
			data["dlist"].append(p)

		# Render template
		path = os.path.join (os.path.dirname (__file__), "template", "list.html")
		self.response.headers ['Content-Type'] = 'text/html'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.out.write (template.render (path, data))

class PageList(webapp2.RequestHandler):
	def get(self, user, durl):
		data = {}
		data = enrich(data)

		from google.appengine._internal.django.utils.safestring import mark_safe
		u = users.get_current_user()

		# Can't see other people's indexes
		if not u:
			self.error(404)
			return

		dq = database.getUserData(user)

		# User inexistant (Wrong url?)
		if not dq:
			self.error(404)
			return

		if (u.nickname() != dq.handler) and (users.is_current_user_admin() == False):
			self.error(404)
			return

		doc = database.getDocument(dq, durl)

		ps = db.Query(model.Page)
		ps.ancestor(doc)

		data["title"] = "Index of " + durl
		data["content"] = "<ul class=\"pageindex\">"
		for x in ps:
			data["content"] += "<li><a href=\"../"+durl+"."+x.surl+"\"><item>"+(x.name if x.name != "" else "[Untitled Page]")+" <i>(<b>"+x.surl+"</b>)</i></item></a></li>"
		data["content"] += "</ul>"
		data["content"] = mark_safe(data["content"]);

		# Render template
		path = os.path.join (os.path.dirname (__file__), "template", "document.html")
		self.response.headers ['Content-Type'] = 'text/html'
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.out.write (template.render (path, data))

class AdminCP(webapp2.RequestHandler):
	def get(self):
		data = {}
		data = enrich(data)
		data["denied"] = True
		# Get user status
		user = users.get_current_user()
		if user:
			data["islogged"] = True
			data["name"] = user.nickname()
			data["url"] = users.create_logout_url("/acp")
			if users.is_current_user_admin():
				data["denied"] = False
		else:
			data["islogged"] = False
			data["url"] = users.create_login_url("/acp")

		# Render template
		path = os.path.join (os.path.dirname (__file__), "template", "admin.html")
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers ['Content-Type'] = 'text/html'
		self.response.out.write (template.render (path, data))
	def post(self):
		# Check priviledges
		if not users.is_current_user_admin():
			self.error(405)
			return

		action = self.request.get('action')

		if action == "adduser":
			nick = self.request.get('nick')
			mail = self.request.get('mail').replace('@gmail.com', '')
			u = model.User(key_name = nick, name = nick, handler = mail)
			u.put()
			self.response.out.write ("done")


class Update(webapp2.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			self.response.out.write("No updates to apply at the moment!")
		else:
			self.error(403)

class PinDocument(webapp2.RequestHandler):
	def post(self, user, durl, page=None):
		u = users.get_current_user()

		# Can't pin other people's docs
		if not u:
			self.error(404)
			return

		dq = database.getUserData(user)

		# User inexistant (Wrong url?)
		if not dq:
			self.error(404)
			return

		if (u.nickname() != dq.handler) and (users.is_current_user_admin() == False):
			self.error(404)
			return

		doc = database.getDocument(dq, durl)
		doc.isfav = (not doc.isfav) if doc.isfav != None else True
		doc.put()
		database.invalidateDocument(dq, doc.surl)

		if doc.isfav:
			self.response.out.write("pinned")
		else:
			self.response.out.write("unpinned")

def enrich(data):
	data["experimental"] = experimental
	return data