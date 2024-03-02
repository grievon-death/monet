import asyncio
import logging
from multiprocessing import Process

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
            _daemons = [
                Process(target=_net.interfaces),
                Process(target=_net.connections)
            ]

            for _d in _daemons:
                _d.start()

            for _d in _daemons:
                _d.join()

        except Exception as e:
            _log.error(e.args)

    @staticmethod
    def test() -> None:
        _net = Network()
        _net.processes()