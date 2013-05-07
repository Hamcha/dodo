import webapp2
import views

app = webapp2.WSGIApplication([
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