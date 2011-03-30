from datetime import datetime, timedelta
from os.path import join, dirname, normpath, relpath, isfile
from random import choice
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
        self.map.connect('index', '/', method='get')
        self.map.connect('static', '/static/{path}', method='static')

    def get(self, request):
        now = datetime.utcnow() + timedelta(hours=-9)
        today = now.date()

        nextgame, nexthomegame = None, None
        for game in schedule:
            if game[0] >= today:
                nextgame = nextgame or game
                if game[1].endswith('at San Francisco'):
                    nexthomegame = game
                    break

        data = {
            'today': today,
            'gametoday': nextgame[0] == today,
            'nextgame': nextgame,
            'nexthomegame': nexthomegame,
            'homegame': nextgame is nexthomegame,
        }

        template = self.jinja.get_template('game.html')
        html = template.render(**data)
        return Response(html, content_type='text/html')

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
