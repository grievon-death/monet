from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from core.app import handler
from settings.config import CONF


class App(Application):
    def __init__(self, port: int) -> None:
        handlers = [
            (r'/api/interfaces/', handler.Interfaces),
            (r'/api/connections/', handler.Connections),
            (r'/api/packages/', handler.Packages),
            (r'/api/login/', handler.Login),
        ]
        settings = dict(
            cookie_secret=CONF.secret_key,
            debug=CONF.debug,
        )
        self.loop = IOLoop.current()
        http_server = HTTPServer(self)
        http_server.listen(port=port)
        super().__init__(handlers, **settings)
