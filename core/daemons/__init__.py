import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime
from threading import Thread
from typing import Any, Dict

import psutil
import pandas as pd
import scapy.all as sp

from core.models.network import Network as NetworkModel
from settings.config import CONF

_log = logging.getLogger(__name__)
_log.setLevel(CONF.log_level)


class Network:
    def __init__(self) -> None:
        self._units = ['', 'K', 'M', 'G', 'T', 'P']
        self._io = psutil.net_io_counters(pernic=True)
        self._macs = { f.mac for f in sp.ifaces.values() }
        self._pid_conn = {}  # Conexão
        self._pid2trfc = defaultdict(lambda: [0, 0])  # Trafego
        self._df = None  # Dataframe global
        self._is_running = True
        self._model = NetworkModel()

    def __get_size(self, _bytes: bytes, _size: int=1024) -> Dict:
        """
        Retorna o tamanho dos bytes num formato legal.
        """
        for unit in self._units:
            if _bytes < _size:
                return f"{_bytes:.2f}{unit}B"
            _bytes /= _size

    def __process_packet(self, packet: Any) -> None:
        """
        Processa o pacote da rede, diferenciando entrada e saída.
        """
        try:
            _pk_connection = (packet.sport, packet.dport)
        except (AttributeError, IndexError):
            # As vezes o pacote não tem layers TCP/UDP, então ignora-se.
            return

        _pk_pid = self._pid2trfc.get(_pk_connection)

        if _pk_pid:
            if packet.src in self._macs:
                # Se tem meu serial é um pacote de saída.
                self._pid2trfc[_pk_pid][0] + len(packet)
            else:
                # Senão pacotes de entrada.
                self._pid2trfc[_pk_pid][1] += len(packet)

    def __get__connections(self) -> None:
        """
        Pega as conexões.
        """
        while self._is_running:
            for _c in psutil.net_connections():
                if _c.laddr and _c.raddr and _c.pid:
                    # Se endereço local e endereço remoto e tem PID
                    # add no dicionário de conexões.
                    self._pid_conn[(_c.laddr.port, _c.raddr.port)] = _c.pid
                    self._pid_conn[(_c.raddr.port, _c.laddr.port)] = _c.pid

    def __print_pid2trafic(self) -> None:
        """
        Mostra os IDs por trafego.
        """
        _processes = []

        for _pid, _trfc in self._pid2trfc.items():
            # `_pid` ID do processo
            # `_trfc` lista com os valores de Download e Upload
            try:
                _proc = psutil.Process(_pid)
            except psutil.NoSuchProcess:
                continue

            try:
                _create_time = datetime.fromtimestamp(_proc.create_time())
            except OSError:
                # Processos do sistema usam o a data de boot
                _create_time = datetime.fromtimestamp(psutil.boot_time())

            _process = {
                'Pid': _pid,
                'Name': _proc.name(),
                'Create time': _create_time,
                'Upload': _trfc[0],
                'Download': _trfc[1], 
            }

            try:
                _process['Upload speed'] = _trfc[0] - self._df.at[_pid, 'Upload']
                _process['Download speed'] = _trfc[1] - self._df.at[_pid, 'Download']
            except (KeyError, AttributeError):
                pass
            
            _processes.append(_processes)

        _dataset = pd.DataFrame(_processes)

        try:
            _dataset = _dataset.set_index("Pid")
            _dataset.sort_values('Download')
        except KeyError as e:
            pass

        _printing_df = _dataset.copy()  # Apenas para printar.

        try:
            _printing_df['Download'] = _printing_df['Download'].apply(self.__get_size)
            _printing_df['Upload'] = _printing_df['Upload'].apply(self.__get_size)
            _printing_df['Download speed'] = _printing_df['Download speed']\
                .apply(self.__get_size)\
                .apply(lambda s: f"{s}/s")
            _printing_df['Upload speed'] = _printing_df['Upload speed']\
                .apply(self.__get_size)\
                .apply(lambda s: f"{s}/s")
        except KeyError:
            pass

        self.__clear()
        print(_printing_df.to_string())
        self._df = _dataset

    def __print_stats(self) -> None:
        """
        Para permanecer printando os status.
        """
        while self._is_running:
            self.__print_pid2trafic()
            time.sleep(CONF.refresh_time)

    async def __interfaces(self) -> None:
        """
        Processa o status de rede das interfaces disponíveis.
        """
        io = psutil.net_io_counters(pernic=True)

        for _if, _if_io in self._io.items():
            uspeed, dspeed = io[_if].bytes_sent - _if_io.bytes_sent, io[_if].bytes_recv - _if_io.bytes_recv
            _data = {
                'interface': _if,
                'download': self.__get_size(io[_if].bytes_recv),
                'updaload': self.__get_size(io[_if].bytes_sent),
                'upload_speed': f'{self.__get_size(uspeed / CONF.refresh_time)}/s',
                'download_speed': f'{self.__get_size(dspeed / CONF.refresh_time)}/s',
                'timestamp': int(datetime.now().timestamp())
            }
            await self._model.set_interfaces(_data)

        self._io = io
        time.sleep(CONF.refresh_time)

    async def processes(self) -> None:
        """
        Mostra o status de rede dos processos em execução.
        """
        _threads = [
            Thread(target=self.__print_stats),
            Thread(target=self.__get__connections),
        ]

        for _t in _threads:
            _t.start()

        sp.sniff(prn=self.__process_packet, store=False)
        self._is_running = False

        for _t in _threads:
            _t.join()

    async def run(self) -> None:
        """
        Executa os daemons de Network.
        """
        while True:
            await self.__interfaces()
