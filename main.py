import webapp2
import views
import dodoapi

app = webapp2.WSGIApplication([
	# APIs
	('/api/user?', dodoapi.GetUser),
	('/api/list([^.]+)?', dodoapi.DocList),
	('/api/read/([^/]+?)/([^/.]+)?(.[^/.]+)?', dodoapi.ViewDocument),
	# Browsable
	('/', views.Homepage),
	('/acp', views.AdminCP),
	('/update', views.Update),
	('/list([^.]+)?', views.DocList),
	('/([^/]+?)/([^/.]+)?(.[^/.]+)?/edit', views.EditDocument),
	('/([^/]+?)/([^/.]+)?(.[^/.]+)?/delete', views.DeleteDocument),
	('/([^/]+?)/([^/.]+)?(.[^/.]+)?/pin', views.PinDocument),
	('/([^/]+?)/([^/.]+)/index', views.PageList),
	('/([^/]+?)/([^/.]+)?(.[^/.]+)?', views.ViewDocument),
], debug=True)