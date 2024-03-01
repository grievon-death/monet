from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from core.app.handler import Interfaces
from settings.config import CONF


class App(Application):
    def __init__(self) -> None:
        handlers = [
            (r'/interfaces/', Interfaces),
        ]
        settings = dict(
            cookie_secret=CONF.secret_key,
            debug=CONF.debug,
        )
        self.loop = IOLoop.current()
        http_server = HTTPServer(self)
        http_server.listen(port=5005)
        super().__init__(handlers, **settings)
