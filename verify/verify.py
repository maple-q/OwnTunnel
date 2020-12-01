#! /usr/bin/python
# coding: utf-8


class ParamsVerify(object):
    def __init__(self, params_dict):
        self.__params_dict = params_dict

        # 端口号上下限
        self.__min_port = 1
        self.__max_port = 65535

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
