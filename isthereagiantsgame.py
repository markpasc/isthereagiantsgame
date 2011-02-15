from google.appengine.dist import use_library
use_library('django', '0.96')

from datetime import datetime, timedelta
from os.path import join, dirname
from random import choice

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from giants_schedule import schedule


class MainPage(webapp.RequestHandler):
    def get(self):
        now = datetime.utcnow() + timedelta(hours=-9)
        today = now.date()

        for game in schedule:
            if game[0] >= today:
                break
        if game[0] < today:
            game = None

        data = {
            'today': today,
            'gametoday': game[0] == today,
            'homegame': game[1].endswith('at San Francisco'),
            'nextgame': game,
        }

        path = join(dirname(__file__), 'html', 'game.html')
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
