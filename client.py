#! /usr/bin/python
# coding: utf-8
from client.client import Client


VERSION = 'v0.2'


def main():
    client = Client()
    try:
        client.start()
    except (KeyboardInterrupt, IOError):
        print('[INFO] Exit now...')
        return


if __name__ == '__main__':
    main()
