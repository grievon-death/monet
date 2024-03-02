import logging
from typing import Any, Dict

from tornado.web import RequestHandler

from core.models.network import Network as NetworkModel

_log = logging.getLogger(__name__)


class Interfaces(RequestHandler):
    """
    Handler da rota de interfaces.
    """
    _model = NetworkModel()

    async def get(self) -> Dict:
        """
        Função para a requisição GET.
        """
        _ifaces = await self._model.get_interfaces()
        self.finish({
            'data': _ifaces
        })


class Connections(RequestHandler):
    """
    Handler da rota de conexões.
    """
    _model = NetworkModel()

    async def get(self) -> Dict:
        _connections = await self._model.get_processes()
        self.finish({
            'data': _connections
        })

class Packages(RequestHandler):
    """
    Handler da rota de pacotes.
    """
    _model = NetworkModel()

    async def get(self) -> Dict:
        _packages = await self._model.get_packages()
        self.finish({
            'data': _packages
        })
