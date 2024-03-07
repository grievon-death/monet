import json
from typing import Dict

from core.models.auth import Auth as AuthModel
from core.models.network import Network as NetworkModel
from core.utils import AuthHash, BaseHandler



###########
# NETWORK #
###########
class Interfaces(BaseHandler):
    """
    Handler da rota de interfaces.
    """
    _model = NetworkModel()

    async def get(self) -> Dict:
        """
        Função para a requisição GET.
        """
        if not await self.is_a_valid_login():
            return

        try:
            _ifaces = await self._model.get_interfaces()
            _filters = self.get_filters()
            self.set_status(200)
            self.finish(self.data_filter(_ifaces, _filters))
        except Exception as e:
            self.set_status(500)
            self.finish({
                'error': e.args
            })


class Connections(BaseHandler):
    """
    Handler da rota de conexões.
    """
    _model = NetworkModel()

    async def get(self) -> Dict:
        if not self.is_a_valid_login():
            return

        try:
            _connections = await self._model.get_processes()
            _filters = self.get_filters()
            self.set_status(200)
            self.finish(self.data_filter(_connections, _filters))
        except Exception as e:
            self.set_status(500)
            self.finish({
                'error': e.args
            })


class Packages(BaseHandler):
    """
    Handler da rota de pacotes.
    """
    _model = NetworkModel()

    async def get(self) -> Dict:
        if not self.is_a_valid_login():
            return

        try:
            _packages = await self._model.get_packages()
            _filters = self.get_filters()
            self.set_status(200)
            self.finish(self.data_filter(_packages, _filters))
        except Exception as e:
            self.set_status(500)
            self.finish({
                'error': e.args
            })


###########
# Usuário #
###########
class User(BaseHandler):
    """
    Handler para a rota de usuários.
    """
    _model = AuthModel()

    async def get(self) -> Dict:
        if not self.is_a_valid_login():
            return

        try:
            _users = await self._model.get_user()
            self.set_status(200)
            self.finish({
                'data': _users
            })
        except Exception as e:
            self.set_status(500)
            self.finish({
                'error': e.args
            })


#########
# Login #
#########
class Login(BaseHandler):
    """
    Handler para a rota de login
    """
    _notfound_msg = 'Incorrect user or password!'
    _invalidpld_msg = 'Invalid payload'
    _model = AuthModel()

    async def post(self) -> Dict:
        """
        Realiza a ação de login.
        """
        _requireds = ['username', 'password']

        try:
            _body = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            self.finish({
                'error': self._invalidpld_msg,
            })
            return

        if not self.have_required_fields(_requireds, _body):
            self.set_status(400)
            self.finish({
                'error': self._invalidpld_msg,
            })
            return

        _usernmame: str=_body['username']
        _password: str=_body['password']

        try:
            _user = await self._model.get_user({
                'username': _usernmame,
            })
        except Exception as e:
            self.set_status(500)
            self.finish({
                'error': e.args
            })
            return

        if not _user or len(_user) != 1:
            self.set_status(400)
            self.finish({
                'error': self._notfound_msg
            })
            return

        _user = _user[0]

        if not AuthHash.passoword_check(_password, _user['password']):
            self.set_status(400)
            self.finish({
                'error': self._notfound_msg
            })
            return

        _token = AuthHash.jtw_generate(_user.copy())
        await self._model.set_token(
            token=_token,
            user_id=_user['_id']
        )

        self.set_status(200)
        self.finish({
            'token': _token
        })
