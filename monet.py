#!/usr/bin/python3.12

"""
Monitoring Network
"""
import asyncio
from argparse import ArgumentParser

from core.network import Network

parser = ArgumentParser(
    description='Network monitor tool.',
)
parser.add_argument(
    'command',
    type=str,
    action='store',
    help='Monitora no formato escolhido. [ default | interfaces | processes ]',
)

if __name__ == '__main__':
    args = parser.parse_args()
    _nt = Network()

    try:
        match args.command:
            case 'default':
                asyncio.run(_nt.speed())
            case 'interfaces':
                asyncio.run(_nt.interfaces())
            case 'processes':
                asyncio.run(_nt.processes())
            case _:
                parser.print_help()

    except KeyboardInterrupt:
        print('Bye ...')
