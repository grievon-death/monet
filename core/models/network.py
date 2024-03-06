import logging
from typing import Dict, List

from pymongo import ASCENDING, DESCENDING, IndexModel, MongoClient
from pymongo.errors import DuplicateKeyError
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

    async def set_interfaces(self, interfaces: List[Dict]) -> None:
        """
        Insere a lista de interfaces no banco de dados.
        """
        if not isinstance(interfaces, (list, tuple)) or not interfaces:
            _log.debug('Invalid interface content.')
            return

        try:
            _result = await self._db.interface.insert_many(interfaces)
        except Exception as e:
            _log.debug(e.args)
        else:
            _log.info('Insert interfaces %s', str(_result.inserted_ids))

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

    async def set_connections(self, connections: List[Dict]) -> None:
        """
        Seta uma conexão.
        """
        if not isinstance(connections, (list, tuple)) or not connections:
            _log.debug('Invalid connection content.')
            return

        try:
            _response = await self._db.process.insert_many(connections)
        except DuplicateKeyError:
            _log.debug('Duplicated connections: %s', str(connections))
        except Exception as e:
            _log.debug(e.args)
        else:
            _log.info('Insert connection %s', _response.inserted_ids)

    async def get_processes(self, query: Dict={}, fields: Dict={}) -> List[Dict]:
        """
        Recupera as conexões salvas no banco.
        """
        if query and not isinstance(query, dict):
            _log.error('Invalid query content.')
            return

        _response = await self._db.process.find(query, fields)\
            .to_list(CONF.db_response_limit)

        if not isinstance(_response, list):
            return []

        for i, r in enumerate(_response):
            _response[i]['_id'] = str(r['_id'])

        return _response

    def set_package(self, package: Dict) -> None:
        """
        Seta os pacotes encontrados no banco de dados.
        """
        if not isinstance(package, dict) or not package:
            _log.debug('Invalid package content.\nContent: %s' % str(package))
            return

        try:
            _db = MongoClient(
                host=CONF.db_host,
                port=CONF.db_port
            )[CONF.db_name]
            _response = _db.package.insert_one(package)
        except Exception as e:
            _log.error(e.args)
        else:
            _log.info('Insert package %s', _response.inserted_id)

    async def get_packages(self, query: Dict={}, fields: Dict={}) -> List[Dict]:
        """
        Recupera as conexões salvas no banco.
        """
        if query and not isinstance(query, dict):
            _log.error('Invalid query content.')
            return
        elif fields and not isinstance(fields, dict):
            _log.debug('Invalid filter content.')
            return

        _response = await self._db.package.find(query, fields)\
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
            _db.process.create_indexes([
                IndexModel([
                    ('expireAfterSeconds', CONF.db_expire_time)
                ]),
                IndexModel([
                    ('local_host', ASCENDING),
                    ('remote_host', DESCENDING),
                    ('pid', DESCENDING)
                ], unique=True)
            ])
            _log.info(_m.format(collection='process'))
        except Exception as e:
            _log.error(e.args)

        try:
            _db.package.create_index({
                'expireAfterSeconds': CONF.db_expire_time
            })
            _log.info(_m.format(collection='package'))
        except Exception as e:
            _log.error(e.args)
