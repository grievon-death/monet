import json
import logging.config as logging

class Config:
    refresh_time: int
    log_level: str
    db_host: str
    db_port: int
    db_name: str
    db_expire_time: int
    db_response_limit: int
    debug: bool
    secret_key: str

    def __init__(self) -> None:
        __content__ = self.__conf_load__()

        try:
            self.refresh_time = __content__.get('refreshTime', 1)
            self.log_level = __content__.get('logLevel', 'info').upper()
            self.db_host = __content__.get('mongoHost', 'mongodb://127.0.0.1')
            self.db_port = __content__.get('mongoPort', 27017)
            self.db_name = __content__.get('mongoName', 'monet')
            self.db_expire_time = __content__.get('mongoExpireDataSeconds', 3600)
            self.db_response_limit = __content__.get('mongoResponseLimit', 100)
            self.debug = __content__.get('debug', False)
            self.secret_key = __content__.get('appSecretKey', 'serw#%@rqdÀWRPA`SDosd123@!13qweqsd-as=-%¨&ÏYJ')
        except KeyError as e:
            print('Miss config propertie!')
            raise Exception(e.args)

    def __conf_load__(self) -> dict:
        """
        Carrega as configurações.
        """
        try:
            with open('conf.json') as r:
                return json.loads(r.read())
        except FileNotFoundError:
            raise Exception('Config file not found!')
        except Exception as e:
            raise Exception(e.args)


CONF = Config()
LOG_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s][%(levelname)s][%(name)s:%(lineno)s] -> %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': CONF.log_level,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'level': CONF.log_level,
            'handlers': ['console'],
            'propagate': False,
        },
        'monet': {
            'level': CONF.log_level,
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
logging.dictConfig(LOG_CONF)
