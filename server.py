#! /usr/bin/python
# coding: utf-8
from server.server import Server


VERSION = 'v0.1'


def main():
    server = Server()
    server.start()


if __name__ == '__main__':
    main()
