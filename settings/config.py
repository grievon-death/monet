import json

class Config:
    refresh_time: int
    log_level: str

    def __init__(self) -> None:
        __content__ = self.__conf_load__()

        try:
            self.refresh_time = __content__['refreshTime']
            self.log_level = __content__.get('logLevel', 'info').upper()
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
