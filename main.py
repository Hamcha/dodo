import webapp2
import views
import dodoapi

app = webapp2.WSGIApplication([

	# APIs
	webapp2.Route(r'/api/user?', handler=dodoapi.GetUser, name='api-get-user'),
	webapp2.Route(r'/api/list<what:(.*)>', handler=dodoapi.DocList, name='api-doc-list'),
	webapp2.Route(r'/api/read/<user>/<durl><page:\.(.+)?>', handler=dodoapi.ViewDocument, name='api-view-doc-full'),
	webapp2.Route(r'/api/read/<user>/<durl>', handler=dodoapi.ViewDocument, name='api-view-doc-home'),
	
	# Browsable
	webapp2.Route(r'/', handler=views.HomePage, name='home'),
	webapp2.Route(r'/home', handler=views.LoginPage, name='login'),
	webapp2.Route(r'/acp', handler=views.AdminCP, name='acp'),
	webapp2.Route(r'/update', handler=views.Update, name='update'),
	webapp2.Route(r'/list<what:(.*)>', handler=views.DocList, name='doc-list'),

	webapp2.Route(r'/<user>/<durl><page:\.(.+)?>/edit', handler=views.EditDocument, name='edit-doc-full'),
	webapp2.Route(r'/<user>/<durl>/edit', handler=views.EditDocument, name='edit-doc-home'),
	webapp2.Route(r'/<user>/<durl><page:\.(.+)?>/delete', handler=views.DeleteDocument, name='delete-doc'),
	webapp2.Route(r'/<user>/<durl><page:\.(.+)?>/pin', handler=views.PinDocument, name='pin-doc-full'),

	webapp2.Route(r'/<user>/<durl>/pin', handler=views.PinDocument, name='pin-doc-home'),
	webapp2.Route(r'/<user>/<durl>/index', handler=views.PageList, name='doc-index'),

	webapp2.Route(r'/<user>/<durl><page:\.(.+)?>', handler=views.ViewDocument, name='view-doc-full'),
	webapp2.Route(r'/<user>/<durl>', handler=views.ViewDocument, name='view-doc-home')
], debug=True)