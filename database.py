from google.appengine.ext import db
from google.appengine.api import memcache
import model

def getUserDataByHandler(handler):
	data = memcache.get('userh:%s' % handler)
	if data:
		return data
	else:
		query = db.Query(model.User)
		query.filter('handler =', handler)
		res = query.get()
		if res != None:
			memcache.set('userh:%s' % handler, res)
		return res

def getUserData(name):
	data = memcache.get('user:%s' % name)
	if data:
		return data
	else:
		res = model.User.get_by_key_name(name)
		if res != None:
			memcache.set('user:%s' % name, res)
		return res

def getDocument(user, durl):
	data = memcache.get('doc:%s:%s' % (user.name ,durl))
	if data:
		return data
	else:
		res = model.Document.get_by_key_name(durl, parent=user)
		if res != None:
			memcache.set('doc:%s:%s' % (user.name ,durl), res)
		return res

def getPage(doc, purl):
	data = memcache.get('page:%s:%s' % (doc.surl, purl))
	if data:
		return data
	else:
		res = model.Page.get_by_key_name(purl, parent=doc)
		if res != None:
			memcache.set('page:%s:%s' % (doc.surl, purl), res)
		return res

def invalidateUser(name):
	return memcache.delete('user:%s' % name)

def invalidateDocument(user, durl):
	return memcache.delete('doc:%s:%s' % (user.name ,durl))

def invalidatePage(doc, purl):
	return memcache.delete('page:%s:%s' % (doc.surl, purl))