from os.path import join, dirname
from random import choice

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template


class MainPage(webapp.RequestHandler):
    def get(self):
        if choice((True, False)):
            filename = 'yes.html'
        else:
            filename = 'no.html'

        data = {}

        path = join(dirname(__file__), 'html', filename)
        html = template.render(path, data)
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(html)


routes = [
    ('/', MainPage),
]

application = webapp.WSGIApplication(routes, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
