import asyncio
import logging

from core.app import App
from core.models.network import Network as NetworkModel
from core.daemons import Network


_log = logging.getLogger(__name__)

class Cmd:
    @staticmethod
    def migrate() -> None:
        _log.info('Starting migrations')
        NetworkModel.migrate()
        _log.info('Stoping migrations')

    @staticmethod
    def run() -> None:
        try:
            _log.info('Starting server.')
            _app = App()
            _app.loop.instance().start()
        except KeyboardInterrupt:
            _log.info('Stoping server.')
            _app.loop.instance().stop()
        except Exception as e:
            _log.error(e.args)

    @staticmethod
    def daemons() -> None:
        _net = Network()
        try:
            asyncio.run(_net.run())
        except Exception as e:
            _log.error(e.args)
