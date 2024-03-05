import logging
from typing import Dict, List

from pymongo import ASCENDING, DESCENDING, IndexModel, MongoClient
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient

from settings.config import CONF

_log = logging.getLogger(__name__)


class Auth:
    def __init__(self) -> None:
        self._db = AsyncIOMotorClient(
            host=CONF.db_host,
            port=CONF.db_port,
        )[CONF.db_name]

    async def set_user(self, user: Dict) -> None:
        """
        Seta um novo usuário no banco de dados.
        """
        if not isinstance(user, dict) or not user:
            _log.error('Invalid user content.')
            return

        try:
            _response = await self._db.user.insert_one(user)
        except DuplicateKeyError:
            _log.warning('The user %s already exists in the system', user['username'])
        except Exception as e:
            _log.error(e.args)
        else:
            _log.info('Created user %s', _response.inserted_id)

    async def get_user(self, query: Dict={}, fields: Dict={}) -> List[Dict]:
        """
        Recupera usuários do banco de dados.
        """
        if query and not isinstance(query, dict):
            _log.debug('Invalid query content.')
            return
        elif fields and not isinstance(fields, dict):
            _log.debug('Invalid filter content.')
            return

        _response = await self._db.user.find(query, fields)\
            .to_list(CONF.db_response_limit)

        if not isinstance(_response, list):
            return []

        for i, r in enumerate(_response):
            _response[i]['_id'] = str(r['_id'])

        return _response

    async def change_user(self, user: Dict) -> None:
        """
        Muda um usuário no banco de dados.
        """
        if not user or not isinstance(user, dict):
            _log.warning('Invalid user content.')
            return

        try:
            _response = await self._db.user.update_one(
                { 'username': user['username'] },
                { '$set': user }
            )
            _log.info('Changed user %s', _response.upserted_id)
        except Exception as e:
            _log.error(e.args)

    @staticmethod
    def find_one(username: str) -> Dict:
        _db = MongoClient(
            host=CONF.db_host,
            port=CONF.db_port,
        )[CONF.db_name]

        return _db.user.find_one({'username': username})

    @staticmethod
    def migrate() -> None:
        """
        Migra as collections responsáveis pelo autenticação de usuário.
        """
        _m = 'Migrate {collection} collection OK.'
        _db = MongoClient(
            host=CONF.db_host,
            port=CONF.db_port,
        )[CONF.db_name]

        try:
            _db.user.create_indexes([
                IndexModel([
                    ('username', ASCENDING),
                    ('token', DESCENDING)
                ], unique=True)
            ])
            _log.info(_m.format(collection='auth'))
            from core.utils import AuthHash
            _db.user.insert_one({
                'username': 'admin',
                'password': AuthHash.password_hash('admin'),
            })
        except Exception as e:
            _log.error(e.args)
