import logging
from typing import Any, Dict, List

from pymongo import DESCENDING, MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

from settings.config import CONF

_log = logging.getLogger(__name__)


class Network:
    """
    Modelo que cuida dos itens no banco de dados.
    """
    _db = AsyncIOMotorClient(
        host=CONF.db_host,
        port=CONF.db_port
    )[CONF.db_name]

    async def set_interfaces(self, interface: Dict) -> None:
        """
        Insere a lista de interfaces no banco de dados.
        """
        if not isinstance(interface, dict):
            _log.error('Invalid interface content.')
            return

        try:
            _result = await self._db.interface.insert_one(interface)
        except Exception as e:
            _log.error(e.args)
        else:
            _log.debug('Insert ObjetId %s', _result.inserted_id)

    async def get_interfaces(self, query: Dict={}, fields: Dict={}) -> List[Dict]:
        """
        Recupera a lista de interfaces do banco de dados.
        """
        _response = []

        if query and not isinstance(query, dict):
            _log.error('Invalid query content.')
            return
        if fields and not isinstance(fields, dict):
            _log.error('Invalid fields for filter.')
            return

        _response = await self._db.interface.find(query, fields)\
            .sort({'timestamp': DESCENDING})\
            .to_list(CONF.db_response_limit)

        if not isinstance(_response, list):
            return []
        
        for i, r in enumerate(_response):
            _response[i]['_id'] = str(r['_id'])
        
        return _response

    @staticmethod
    def migrate() -> None:
        """
        Cria o modelo das coleções.
        """
        _db = MongoClient(
            host=CONF.db_host,
            port=CONF.db_port
        )[CONF.db_name]
        _m = 'Migrate {collection} collection OK.'

        try:
            _db.interface.create_index({
                'expireAfterSeconds': CONF.db_expire_time
            })
            _log.info(_m.format(collection='trafic'))
        except Exception as e:
            _log.error(e.args)

        try:
            _db.process.create_index({
                'expireAfterSeconds': CONF.db_expire_time
            })
            _log.info(_m.format(collection='process'))
        except Exception as e:
            _log.error(e.args)
