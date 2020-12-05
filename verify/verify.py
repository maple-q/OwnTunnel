#! /usr/bin/python
# coding: utf-8


class ParamsVerify(object):
    def __init__(self, params_dict):
        self.__params_dict = params_dict

        # 端口号上下限
        self.__min_port = 1
        self.__max_port = 65535

        # IP地址上下限
        self.__min_nums = 0
        self.__max_nums = 255

    def verify(self):
        """
        参数校验，如果参数传递问题，则抛出异常
        :return:
        """
        listen_port = self.__params_dict['listen_port']
        self.__verify_port(listen_port)

        trans_port = self.__params_dict['trans_port']
        self.__verify_port(trans_port)

    def __verify_port(self, port):
        """
        校验port是否符合要求，不符合要求则抛出异常
        :param port: 端口
        :return:
        """
        try:
            port = int(port)
        except ValueError:
            raise Exception('port should only contains integer')
        else:
            if port < self.__min_port or port > self.__max_port:
                raise Exception('port should in [1, 65535]')

    def __verify_address(self, address):
        """
        校验IP地址是否符合要求，不符合抛出异常
        :param address: IP地址
        :return:
        """
        split_address = address.split('.')
        if len(split_address) != 4:
            raise Exception('Invalid IP Address!')

        for addr in split_address:
            try:
                addr = int(addr)
                if addr < self.__min_nums or addr > self.__max_nums:
                    raise Exception('Invalid IP Address')
            except Exception:
                raise Exception('Invalid IP Address')

    def client_param_verify(self):
        """
        OwnTunnel客户端参数校验
        :return:
        """
        own_tunnel_port = self.__params_dict['own_tunnel_port']
        self.__verify_port(own_tunnel_port)

        dst_port = self.__params_dict['dst_port']
        self.__verify_port(dst_port)

        # 校验IP地址
        own_tunnel_server = self.__params_dict['own_tunnel_server']
        self.__verify_address(own_tunnel_server)

        dst_server = self.__params_dict['dst_server']
        self.__verify_address(dst_server)
