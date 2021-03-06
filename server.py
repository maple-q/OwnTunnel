#! /usr/bin/python
# coding: utf-8
from server.server import Server


VERSION = 'v0.2'


def main():
    server = Server()
    try:
        server.start()
    except (KeyboardInterrupt, IOError):
        print('[INFO] Exit now...')
        return


if __name__ == '__main__':
    main()
