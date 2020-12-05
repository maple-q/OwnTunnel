#! /usr/bin/python
# coding: utf-8
import argparse


class ParamsParser(object):
    def __init__(self):
        self.__params = self.__add_default_params()

    @staticmethod
    def __add_default_params():
        """
        添加默认参数
        :return:
        """
        parser = argparse.ArgumentParser(description='Transfer Server')

        parser.add_argument('-p', '--port', dest='listen_port', action='store', required=True,
                            help="Listen Port for waiting client's connect.")
        parser.add_argument('-t', '--trans-port', dest='trans_port', action='store', required=True,
                            help='Listen Port for transfer data to another listening port.')
        parser.add_argument('-vv', dest='detail_log', action='store_true', help='output more logs')

        args = parser.parse_args()

        params = {
            'listen_port': args.listen_port,
            'trans_port': args.trans_port,
            'detail_log': args.detail_log,
        }

        return params

    def get_params(self):
        return self.__params
