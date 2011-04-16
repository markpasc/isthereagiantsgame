from datetime import datetime, timedelta
from os.path import join, dirname, normpath, relpath, isfile
from random import choice
import re
import mimetypes
import sys
from traceback import format_exception

from jinja2 import Environment, FileSystemLoader
from routes import Mapper, URLGenerator
from webob import Response
from webob.dec import wsgify
from webob.exc import HTTPNotFound

from giants_schedule import schedule


class Application(object):

    def __init__(self):
        path = join(dirname(__file__), 'html')
        self.jinja = Environment(loader=FileSystemLoader(path))

        self.static_path = join(dirname(__file__), 'static')

        self.map = Mapper()
        self.map.connect('index', '/{when:[^/]*}', method='get')
        self.map.connect('api', '/api/{when}', method='api')
        self.map.connect('static', '/static/{path}', method='static')

    def day_for_when(self, when):
        mo = re.match(r'(\d{4})(\d{2})(\d{2})', when)
        if mo is not None:
            year, month, day = [int(mo.group(i)) for i in range(1, 4)]
            return datetime(year=year, month=month, day=day).date()

        now = datetime.utcnow() + timedelta(hours=-9)
        today = now.date()
        when = when.lower()

        if not when or when == 'today':
            return today

        if when == 'tomorrow':
            return today + timedelta(days=1)

        for addl_days in xrange(1, 8):
            maybe_today = today + timedelta(days=addl_days)
            if when in [maybe_today.strftime(x).lower() for x in ('%a', '%A')]:
                return maybe_today

    def nextgames(self, today):
        nextgame, nexthomegame = None, None
        for game in schedule:
            if game[0] >= today:
                nextgame = nextgame or game
                if game[1].endswith('at San Francisco'):
                    nexthomegame = game
                    break
        return nextgame, nexthomegame

    def get(self, request, when):
        today = self.day_for_when(when)
        if today is None:
            return HTTPNotFound()
        nextgame, nexthomegame = self.nextgames(today)

        data = {
            'today': today,
            'gametoday': nextgame[0] == today,
            'nextgame': nextgame,
            'nexthomegame': nexthomegame,
            'homegame': nextgame is nexthomegame,
            'root_url': '://'.join(request.environ[x] for x in ('wsgi.url_scheme', 'HTTP_HOST')),
        }

        template = self.jinja.get_template('game.html')
        html = template.render(**data)
        return Response(html, content_type='text/html')

    def api(self, request, when):
        today = self.day_for_when(when)
        if today is None:
            return Response("no such day '%s'" % when, status=400, content_type='text/plain')
        nextgame, nexthomegame = self.nextgames(today)
        if nextgame[0] == today:
            if nextgame is nexthomegame:
                return Response("yes", status=200, content_type='text/plain')
            return Response(status=204)
        return Response(nextgame[0].strftime("next home game %Y%m%d"), status=404, content_type='text/plain')

    def static(self, request, path):
        # Does the file exist?
        diskpath = normpath(join(self.static_path, path))
        if relpath(diskpath, self.static_path).startswith('..'):
            return HTTPNotFound()
        if not isfile(diskpath):
            return HTTPNotFound()

        # Serve it (dumbly).
        filetype, encoding = mimetypes.guess_type(path)
        res = Response(content_type=filetype or 'application/octet-stream')
        res.body = open(diskpath, 'rb').read()
        return res

    @wsgify
    def __call__(self, request):
        try:
            results = self.map.routematch(environ=request.environ)
            if not results:
                return HTTPNotFound()
            match, route = results
            link = URLGenerator(self.map, request.environ)
            request.urlvars = ((), match)
            kwargs = match.copy()
            method = kwargs.pop('method')
            request.link = link

            return getattr(self, method)(request, **kwargs)
        except Exception:
            return Response('\n'.join(format_exception(*sys.exc_info())), content_type='text/plain')


application = Application()

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    server = make_server('127.0.0.1', 8080, application)
    server.serve_forever()
