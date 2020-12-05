# /usr/bin/env python
# coding: utf-8
import random
import sys
import socket
import time
import threading

from io_handle.client_params import ParamsParser
from verify.verify import ParamsVerify
from logs.logs import Log
from constant.constant import Constant


class Client(object):
    def __init__(self):
        # 参数解析，ParamsParser类应该返回解析后的参数字典
        self.__param_parser = ParamsParser()

        self.__params = self.__param_parser.get_params()
        # 参数校验
        self.__param_verify = ParamsVerify(self.__params)

        try:
            self.__param_verify.client_param_verify()
        except Exception as e:
            sys.stdout.write(e.message)
            sys.exit(-1)

        # 完成以上步骤，得到两组远程ip + port
        self.__own_tunnel_server = self.__params['own_tunnel_server']
        self.__own_tunnel_port = int(self.__params['own_tunnel_port'])
        self.__dst_server = self.__params['dst_server']
        self.__dst_port = int(self.__params['dst_port'])

        # 得到日志选项，默认关闭，如果开启，需要指定 -vv 参数
        self.__log_opened = self.__params['detail_log']
        print(self.__log_opened)

        self.log_obj = Log(self.__log_opened)

        # 缓冲区大小
        self.__buffer_size = 1 * 1024

        # 连接失败重新尝试连接次数
        self.__retry_max = 5

        # 随机休眠时间
        self.__random_sleep_time = 3

    def start(self):
        self.log_obj.log(Constant.INFO, 'Client Starting now...')

        while True:
            own_tunnel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                own_tunnel_socket.connect((self.__own_tunnel_server, self.__own_tunnel_port))
            except socket.error:
                self.log_obj.log_optional(Constant.INFO, 'connect to {}:{} failed'.format(self.__own_tunnel_server,
                                                                                          self.__own_tunnel_port))
                time.sleep(random.randint(1, self.__random_sleep_time))
                continue

            dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                dst_socket.connect((self.__dst_server, self.__dst_port))
            except socket.error:
                self.log_obj.log_optional(Constant.INFO, 'connect to {}:{} failed'.format(self.__dst_server,
                                                                                          self.__dst_port))
                continue

            self.log_obj.log(Constant.INFO, 'forwarding data: {}:{}   <=>   {}:{}'.format(self.__own_tunnel_server,
                                                                                          self.__own_tunnel_port,
                                                                                          self.__dst_server,
                                                                                          self.__dst_port))

            own_tunnel_to_dst_thread = threading.Thread(target=self.forward_from_dst_to_own, args=(own_tunnel_socket,
                                                                                                   dst_socket))
            dst_to_own_tunnel_thread = threading.Thread(target=self.forward_from_dst_to_own, args=(dst_socket,
                                                                                                   own_tunnel_socket))
            own_tunnel_to_dst_thread.setDaemon(True)
            dst_to_own_tunnel_thread.setDaemon(True)

            # 开启线程，接收到空时，重新建立连接
            own_tunnel_to_dst_thread.start()
            dst_to_own_tunnel_thread.start()

    def forward_from_own_to_dst(self, own_tunnel_socket, dst_socket):
        """
        读own_tunnel_socket数据，写入dst_socket
        :param own_tunnel_socket:
        :param dst_socket:
        :return:
        """
        # TODO 之后在OwnTunnel CS端可能会进行加密传输，将两个函数分离出来主要为了后续的解密处理
        while True:
            try:
                read_data = own_tunnel_socket.recv(self.__buffer_size)
            except socket.error:
                self.log_obj.log(Constant.WARN, 'recv data from {}:{} failed.'.format(self.__dst_server, self.__dst_port))
                break

            if not read_data:
                break

            try:
                dst_socket.send(read_data)
            except socket.error:
                self.log_obj.log(Constant.WARN, 'send data to {}:{} failed.'.format(self.__dst_server, self.__dst_port))
                break

    def forward_from_dst_to_own(self, dst_socket, own_tunnel_socket):
        """
        读dst_socket数据，转发到own_tunnel_socket
        :param dst_socket:
        :param own_tunnel_socket:
        :return:
        """
        while True:
            try:
                read_data = dst_socket.recv(self.__buffer_size)
            except socket.error:
                self.log_obj.log(Constant.WARN, 'recv data from {}:{} failed.'.format(self.__dst_server,
                                                                                      self.__dst_port))
                break

            if not read_data:
                break

            try:
                own_tunnel_socket.send(read_data)
            except socket.error:
                self.log_obj.log(Constant.WARN, 'send data to {}:{} failed.'.format(self.__own_tunnel_server,
                                                                                    self.__own_tunnel_port))
                break
