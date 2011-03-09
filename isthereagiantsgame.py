from google.appengine.dist import use_library
use_library('django', '0.96')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class MainPage(webapp.RequestHandler):
    def get(self):
        self.redirect('http://isthereagiantsga.me/', permanent=True)


routes = [
    ('/', MainPage),
]

application = webapp.WSGIApplication(routes, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
