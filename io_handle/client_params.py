#! /usr/bin/python
# coding: utf-8
import argparse


class ParamsParser(object):
    """OwnTunnel Client端命令行参数校验"""

    def __init__(self):
        self.__params = self.__add_default_params()

    @staticmethod
    def __add_default_params():
        """
        添加默认参数
        :return:
        """
        parser = argparse.ArgumentParser(description='OwnTunnel Client')

        parser.add_argument('-ts', '--tunnel-server', dest='own_tunnel_server', action='store', required=True,
                            help="Remote OwnTunnel Server IP")
        parser.add_argument('-tp', '--tunnel-port', dest='own_tunnel_port', action='store', required=True,
                            help='Remote OwnTunnel Server Port')
        parser.add_argument('-ds', '--dst-server', dest='dst_server', action='store', required=True,
                            help="Destination Server IP")
        parser.add_argument('-dp', '--dst-port', dest='dst_port', action='store', required=True,
                            help='Destination Server Port')
        parser.add_argument('-vv', dest='detail_log', action='store_true', help='output more logs')

        args = parser.parse_args()

        params = {
            'own_tunnel_server': args.own_tunnel_server,
            'own_tunnel_port': args.own_tunnel_port,
            'dst_server': args.dst_server,
            'dst_port': args.dst_port,
            'detail_log': args.detail_log,
        }

        return params

    def get_params(self):
        return self.__params
