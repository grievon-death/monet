import logging
from typing import Any, Dict

from tornado.web import RequestHandler

from core.models.network import Network as NetworkModel

_log = logging.getLogger(__name__)


class Interfaces(RequestHandler):
    """
    Handler da rota 
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

