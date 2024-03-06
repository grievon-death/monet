import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict

import psutil
import scapy.all as sp

from core.models.network import Network as NetworkModel
from settings.config import CONF

_log = logging.getLogger(__name__)
_log.setLevel(CONF.log_level)


class Network:
    def __init__(self) -> None:
        self._units = ['', 'K', 'M', 'G', 'T', 'P']
        self._io = psutil.net_io_counters(pernic=True)
        self._model = NetworkModel()

    async def __interfaces(self) -> None:
        """
        Processa o status de rede das interfaces disponíveis.
        """
        _interfaces = []
        
        while True:
            io = psutil.net_io_counters(pernic=True)

            for _if, _if_io in self._io.items():
                uspeed, dspeed = io[_if].bytes_sent - _if_io.bytes_sent, io[_if].bytes_recv - _if_io.bytes_recv
                _interfaces.append({
                    'interface': _if,
                    'download': io[_if].bytes_recv,
                    'updaload': io[_if].bytes_sent,
                    'upload_speed': (uspeed / CONF.refresh_time),
                    'download_speed': (dspeed / CONF.refresh_time),
                    'timestamp': datetime.now().timestamp()
                })

            await self._model.set_interfaces(_interfaces)
            self._io = io
            time.sleep(CONF.refresh_time)
            _interfaces.clear()

    async def __connections(self) -> None:
        """
        Pega as conexões.
        """
        _connections = []

        while True:
            for _c in psutil.net_connections():
                if _c.laddr and _c.raddr and _c.pid:
                    # Se endereço local e endereço remoto e tem PID
                    # add no dicionário de conexões.
                    _connections.append({
                        'local_host': f'{_c.laddr.ip}:{_c.laddr.port}',
                        'remote_host': f'{_c.raddr.ip}:{_c.raddr.port}',
                        'pid': _c.pid,
                        'status': _c.status,
                    })

            await self._model.set_connections(_connections)
            time.sleep(CONF.refresh_time)
            _connections.clear()

    def __pkg_process(self, package: Any) -> None:
        """
        Insere os pacotes da máquina em uma collection.
        """
        _pkg = {
            'interface': package.name,
            'source': package.src,
            'destiny': package.dst,
            'pkg_len': len(package),
            'timestamp': package.time,
        }
        self._model.set_package(_pkg)

    # As funções a baixo são necessárias para rodar os daemons em processos separados.
    # O multiprocessing do python não aceita funções assíncronas.

    def interfaces(self) -> None:
        asyncio.run(self.__interfaces())

    def connections(self) -> None:
        asyncio.run(self.__connections())

    def processes(self) -> None:
        """
        Salva os dados dos processos do sistema.
        """
        try:
            sp.sniff(prn=self.__pkg_process, store=False)
        except PermissionError:
            _log.warning('Operation not permited!')
        except Exception as e:
            _log.error(e.args)