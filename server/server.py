#! /usr/bin/python
# coding: utf-8
import random
import sys
import socket
import time
import threading

from collections import deque

from io_handle.server_params import ParamsParser
from verify.verify import ParamsVerify
from constant.constant import Constant
from logs.logs import Log


class Server(object):
    def __init__(self):
        # 参数解析，ParamsParser类应该返回解析后的参数字典
        self.__param_parser = ParamsParser()

        self.__params = self.__param_parser.get_params()
        # 参数校验
        self.__param_verify = ParamsVerify(self.__params)

        try:
            self.__param_verify.verify()
        except Exception as e:
            sys.stdout.write(e.message)
            sys.exit(-1)

        # 完成上面步骤，可以开始监听端口
        self.__listen_host = '0.0.0.0'
        # 通过端口检验，即可获取两个监听端口
        self.__listen_port = int(self.__params['listen_port'])
        self.__trans_port = int(self.__params['trans_port'])
        # 日志等级
        self.__log_opened = self.__params['detail_log']
        self.__log_obj = Log(self.__log_opened)

        # socket 已完成握手的最大队列数量
        self.__max_queue_nums = 5

        # TCP接受缓冲区大小
        self.__read_buffer_size = 1 * 1024

        self.__OWN_TUNNEL_CLIENT = 'own_tunnel_client'
        self.__USER_CLIENT = 'user_client'

    def start(self):
        self.__log_obj.log(Constant.INFO, 'Starting Server now...')

        # 先监听和Own Tunnel连接的端口，再监听和用户端连接端口
        while True:
            connections_queue = deque(maxlen=2)

            thread1 = threading.Thread(target=self.listen_tunnel, args=(connections_queue, ))
            thread1.setDaemon(True)

            thread2 = threading.Thread(target=self.listen_user_port, args=(connections_queue, ))
            thread2.setDaemon(True)

            thread2.start()
            thread1.start()

            while True:
                if len(connections_queue) != 2:
                    continue
                else:
                    break

            # 从队列取出两个套接字
            own_tunnel_client_socket, user_client_socket = None, None
            for connections in connections_queue:
                if self.__OWN_TUNNEL_CLIENT == connections.keys()[0]:
                    own_tunnel_client_socket = connections[connections.keys()[0]]

                if self.__USER_CLIENT == connections.keys()[0]:
                    user_client_socket = connections[connections.keys()[0]]

            # 开启两个线程执行转发
            own_client_to_user_thread = threading.Thread(target=self.forward_from_own_client_to_user,
                                                         args=(own_tunnel_client_socket, user_client_socket))
            own_client_to_user_thread.setDaemon(True)

            user_to_own_client_thread = threading.Thread(target=self.forward_from_user_to_own_client,
                                                         args=(user_client_socket, own_tunnel_client_socket))
            user_to_own_client_thread.setDaemon(True)

            own_client_to_user_thread.start()
            user_to_own_client_thread.start()

    def listen_tunnel(self, connections_queue):
        """
        监听和OwnTunnel通信的端口
        :param connections_queue:
        :return:
        """
        own_tunnel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        own_tunnel_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while True:
            try:
                own_tunnel_socket.bind((self.__listen_host, self.__listen_port))
            except socket.error:
                self.__log_obj.log(Constant.INFO, 'binding {}:{} failed, please check the port has been listened.'
                                   .format(self.__listen_host, self.__listen_port))
                time.sleep(random.randint(1, 3))
                continue

            own_tunnel_socket.listen(self.__max_queue_nums)
            self.__log_obj.log(Constant.INFO, 'Server Listen at {}:{} now...'.format(self.__listen_host,
                                                                                     self.__listen_port))

            # 开启监听
            own_tunnel_client_socket, own_tunnel_client_addr = own_tunnel_socket.accept()
            self.__log_obj.log(Constant.INFO, 'client {}:{} connected.'.format(own_tunnel_client_addr[0],
                                                                               own_tunnel_client_addr[1]))

            connections_queue.append({self.__OWN_TUNNEL_CLIENT: own_tunnel_client_socket})
            break

    def listen_user_port(self, connections_queue):
        """
        监听和user端通信的端口
        :param connections_queue:
        :return:
        """
        user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        user_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while True:
            try:
                user_socket.bind((self.__listen_host, self.__trans_port))
            except socket.error:
                self.__log_obj.log(Constant.INFO, 'binding {}:{} failed, please check the port has been listened.'
                                   .format(self.__listen_host, self.__trans_port))
                time.sleep(random.randint(1, 3))
                continue

            user_socket.listen(self.__max_queue_nums)
            self.__log_obj.log(Constant.INFO, 'Server Listen at {}:{} now...'.format(self.__listen_host,
                                                                                     self.__trans_port))

            # 开启监听
            user_client_socket, user_client_addr = user_socket.accept()

            connections_queue.append({self.__USER_CLIENT: user_client_socket})
            break

    def forward_from_own_client_to_user(self, own_tunnel_client_socket, user_socket):
        """
        读own_tunnel_client，写user_socket
        :param own_tunnel_client_socket:
        :param user_socket:
        :return:
        """
        # TODO 从OwnTunnel Client发送的数据后续加密，这里将两个函数拆分主要为了后续考虑
        while True:
            try:
                read_data = own_tunnel_client_socket.recv(self.__read_buffer_size)
            except socket.error:
                break

            # 没有data可读，则线程结束
            if not read_data:
                break

            try:
                user_socket.send(read_data)
            except socket.error:
                break

    def forward_from_user_to_own_client(self, user_socket, own_tunnel_client_socket):
        """
        读user_socket，写own_tunnel_client_socket
        :param user_socket:
        :param own_tunnel_client_socket:
        :return:
        """
        while True:
            try:
                read_data = user_socket.recv(self.__read_buffer_size)
            except socket.error:
                break

            # 没有data可读，则线程结束
            if not read_data:
                break

            try:
                own_tunnel_client_socket.send(read_data)
            except socket.error:
                break
