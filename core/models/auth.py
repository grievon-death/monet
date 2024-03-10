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

    async def set_user(self, user: Dict) -> str | None:
        """
        Seta um novo usuário no banco de dados.
        """
        if not isinstance(user, dict) or not user:
            _log.error('Invalid user content.')
            return

        try:
            _response = await self._db.user.insert_one(user)
        except DuplicateKeyError as e:
            _log.warning('The user %s already exists in the system', user['username'])
            raise e
        except Exception as e:
            _log.error(e.args)
            raise e
        else:
            _log.info('Created user %s', _response.inserted_id)
            return str(_response.inserted_id)

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

    async def change_user(self, user: Dict) -> str | None:
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

    async def get_token(self, user_id: str) -> str | None:
        """
        Recupera o token do banco de dados.
        """
        if not isinstance(user_id, str):
            _log.debug('Invalid token!')
            return

        try:
            _response = await self._db.token.find_one({
                'user': user_id
            })
        except Exception as e:
            _log.error(e.args)

        try:
            return _response['token']
        except KeyError:
            return

    async def set_token(self, token: str, user_id: str) -> None:
        """
        Insere o token do banco de dados.
        """
        if not isinstance(token, str):
            return

        try:
            _user = await self._db.token.find_one({'user': user_id})
        except Exception as e:
            _log.error(e.args)
            return

        if not _user:
            try:
                _response = await self._db.token.insert_one({
                    'token': token,
                    'user': user_id,
                })
                _log.debug('Inserted token: %s', _response.inserted_id)
            except Exception as e:
                _log.error(e.args)
                return
        else:
            try:
                _response = await self._db.token.update_one(
                    { 'user': user_id },
                    { '$set': { 'token': token }}
                )
                _log.debug('Inserted token: %s', _response.upserted_id)
            except Exception as e:
                _log.error(e.args)

    async def find_one(self, username: str) -> Dict | None:
        _response = await self._db.user.find_one({'username': username})

        if _response:
            _response['_id'] = str(_response['_id'])

        return _response

    async def remove_one(self, username: str) -> int | None:
        """
        Remove um usuário.
        """
        try:
            _response = await self._db.user.delete_one({
                'username': username
            })
            _log.debug('User %s removed. (%s)' % (username, _response.deleted_count))
            return _response.deleted_count
        except Exception as e:
            _log.error(e.args)
            raise e

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
                    ('username', ASCENDING)
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

        try:
            _db.token.create_indexes([
                IndexModel([
                    ('token', DESCENDING),
                    ('user_id', DESCENDING),
                ], unique=True)
            ])
            _log.info(_m.format(collection='token'))
        except Exception as e:
            _log.error(e.args)
