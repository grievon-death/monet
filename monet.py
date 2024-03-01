#!/usr/bin/python3.12

"""
Monitoring Network
"""
import logging
from argparse import ArgumentParser

from core.commands import Cmd

parser = ArgumentParser(
    description='Network monitor tool.',
)
parser.add_argument(
    'command',
    type=str,
    action='store',
    help='Comando do serviço a ser executado. [ daemon | migrate | run ]',
)

if __name__ == '__main__':
    _log = logging.getLogger(__name__)
    args = parser.parse_args()

    try:
        match args.command:
            case 'run':
                Cmd.run()
            case 'migrate':
                Cmd.migrate()
            case 'daemon':
                Cmd.daemons()
            case _:
                parser.print_help()

    except KeyboardInterrupt:
        _log.info('Bye ...')
    except Exception as e:
        _log.error(e.args)
