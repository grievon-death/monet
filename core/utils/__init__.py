import json
import logging
from datetime import datetime, timedelta
from hashlib import pbkdf2_hmac
from typing import Any, Dict, List

import jwt
from tornado.web import RequestHandler

from core.models.auth import Auth as AuthModel
from core.utils import errors
from settings.config import CONF

_log = logging.getLogger(__name__)


class AuthHash:
    """
    Classe que auxilia na criptografia e hash.
    """
    @staticmethod
    def password_hash(password: str) -> str:
        """
        Faz uma hash para a senha.
        """
        _pwd = pbkdf2_hmac(
            hash_name='sha256',
            password=password.encode(),
            salt=CONF.secret_key.encode(),
            iterations=5,
        ).hex()
        return _pwd

    @staticmethod
    def passoword_check(password: str, hashed: str) -> bool:
        """
        Checa se a senha está correta.
        """
        _pwd = pbkdf2_hmac(
            hash_name='sha256',
            password=password.encode(),
            salt=CONF.secret_key.encode(),
            iterations=5,
        ).hex()

        return _pwd == hashed

    @staticmethod
    def jtw_generate(content: Dict) -> str:
        """
        Gera um token web JWT.
        """
        content['exp'] = int(datetime.now().timestamp() + timedelta(hours=8).total_seconds())
        return jwt.encode(content, CONF.secret_key, algorithm='HS256')

    @staticmethod
    def jwt_recover(token: str) -> Dict:
        """
        Retorna o conteúdo do token JWT.
        """
        try:
            return jwt.decode(token, CONF.secret_key, algorithms=['HS256'])
        except jwt.exceptions.ExpiredSignatureError as e:
            _log.warning('Expired token!')
            raise e


class Tools:
    """
    Ferramentas gerais.
    """
    @staticmethod
    def have_required_fields(requireds: List[Any], body: Dict) -> bool:
        """
        Checa se tem todos os campos obrigatórios.
        """
        if any([k not in requireds for k in body.keys()]):
            return False
        elif not all([r in body.keys() for r in requireds]):
            return False
        return True


class BaseHandler(RequestHandler):
    def __login_validation(self) -> Exception | None:
        """
        Função que checa se o login é valido.
        """
        try:
            _headers = self.request.headers._dict
        except Exception as e:
            _log.debug(e.args)
            raise errors.MissAuthorization('Invalid request header!')

        _token = _headers.get('Authorization')

        if not _token:
            _msg = 'Empty authorization token!'
            _log.warning(_msg)
            raise errors.MissAuthorization(_msg)

        try:
            _tkn = AuthHash.jwt_recover(_token)
        except (
            jwt.exceptions.ExpiredSignatureError,
            jwt.exceptions.DecodeError,
            jwt.exceptions.ExpiredSignatureError,
            jwt.exceptions.InvalidSignatureError,
            jwt.exceptions.InvalidKeyError,
            jwt.exceptions.InvalidTokenError,
        ) as e:
            _log.error(e.args)
            raise errors.InvalidToken('Invalid token!')

        try:
            _user = AuthModel.find_one(username=_tkn['username'])
        except KeyError:
            _msg = 'Token required field not found.'
            _log.error(_msg)
            raise errors.InvalidToken(_msg)

        if not _user:
            _msg = 'Invalid username!'
            _log.error(_msg)
            raise errors.InvalidToken(_msg)

        _u_tkn = _user.get('token')

        _msg = 'Invalid token!'

        if not _u_tkn:
            _log.error(_msg)
            raise errors.InvalidToken(_msg)
        elif not _u_tkn ==  _token:
            _log.error(_msg)
            raise errors.InvalidToken(_msg)

    def is_a_valid_login(self) -> bool:
        """
        Decorator de validação.
        """
        try:
            self.__login_validation()
        except errors.InvalidToken as e:
            self.set_status(status_code=400)
            self.finish({
                'error': e.args
            })
            return False
        except errors.InvaliUser as e:
            self.set_status(status_code=400)
            self.finish({
                'error': e.args
            })
            return False
        except errors.MissAuthorization as e:
            self.set_status(status_code=400)
            self.finish({
                'error': e.args
            })
            return False
        except Exception as e:
            self.set_status(status_code=400)
            _log.debug(e.args)
            self.finish({
                'error': 'Unspected error!'
            })
            return False

        return True
