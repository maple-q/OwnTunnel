#! /usr/bin/python
# coding: utf-8
import sys
import socket
import threading

from io_handle.params import ParamsParser
from verify.verify import ParamsVerify


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

        # socket 已完成握手的最大队列数量
        self.__max_queue_nums = 5

        # 两个列表，一个存放连接trans口的客户端，一个存放连接listen口的客户端
        self.__trans_client = list()
        # [(socket1, addr1), (socket2, addr2)]
        # [(socket3, addr3), (socket4, addr4)]
        # 此时socket1和socket3通信，socket2和socket4通信，如果两个列表长度不相等，则多出来的socket发送的数据将被丢弃
        self.__listen_client = list()

        # 互斥锁，往列表中添加client时需要加锁，消费client也需要加锁
        self.__mutex = threading.Semaphore(1)
        # TCP接受缓冲区大小
        self.__read_buffer_size = 4 * 1024

    def start(self):
        print('[INFO] Server starting now...')
        print('[INFO] Listen Port: {listen_port}, Trans Port: {trans_port}'.format(listen_port=self.__listen_port,
                                                                                   trans_port=self.__trans_port))

        # 开启两个线程，分别监听两个端口
        trans_thread = threading.Thread(target=self.listen, args=(self.__trans_port, self.__trans_client))
        listen_thread = threading.Thread(target=self.listen, args=(self.__listen_port, self.__listen_client))
        # 再开启以下线程，循环读取两个列表相应位置上的套接字，并创建线程在其之间传递数据
        consumer_thread = threading.Thread(target=self.consumer)

        trans_thread.start()
        listen_thread.start()
        consumer_thread.start()
        # 主线程等待
        trans_thread.join()
        listen_thread.join()
        consumer_thread.join()

    def listen(self, port, client_collection):
        """
        监听端口，等待客户端连接
        :param port: 需要监听的端口
        :param client_collection: 一旦有客户端连接，则将其加入到列表中
        :return:
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO 禁用Nagle算法 需要测试禁用之后是否还存在粘包问题
        server_socket.bind((self.__listen_host, port))
        server_socket.listen(self.__max_queue_nums)

        # 开启等待
        while True:
            remote_socket, remote_addr = server_socket.accept()
            print('===========================================')
            print('[INFO] Client: {remote_ip}: {remote_port} connected.'.format(remote_ip=remote_addr[0],
                                                                                remote_port=remote_addr[1]))

            # TODO 这里很纠结呀，两个端口同时监听，如果两个端口各自有1个客户端连接，那直接转发数据就可以了
            # TODO 但是，如果两个端口都不止一个客户端连接，怎么处理？
            # TODO 能不能用数据结构来进行维护，先尝试用两个列表来进行维护
            self.__mutex.acquire()
            client_collection.append((remote_socket, remote_addr))
            self.__mutex.release()

    def consumer(self):
        """
        消费者进程，读取存放了多个客户端的列表，从中取出相对应位置上的
        :return:
        """
        while True:
            # 这里消费需要加锁，如果不加锁，在长度判断之后，其他线程可能会写入列表，导致当前线程后续执行出错
            self.__mutex.acquire()

            trans_client_length = len(self.__trans_client)
            listen_client_length = len(self.__listen_client)

            if trans_client_length != 0 and trans_client_length == listen_client_length:
                for trans_client, listen_client in zip(self.__trans_client, self.__listen_client):
                    print('[INFO] trans data from {} to {}'.format(trans_client[1], listen_client[1]))
                    threading.Thread(target=self.forward, args=(trans_client, listen_client)).start()

                    print('[INFO] trans data from {} to {}'.format(listen_client[1], listen_client[1]))
                    threading.Thread(target=self.forward, args=(listen_client, trans_client)).start()

                self.__trans_client.clear()
                self.__listen_client.clear()

            # 释放锁
            self.__mutex.release()

    def forward(self, socket_to_read, socket_to_write):
        """
        从socket_to_read中读取内容，转发到socket_to_write
        :param socket_to_read: 读socket
        :param socket_to_write: 写socket
        :return:
        """
        while True:
            try:
                # TODO 从socket读取时，缓冲区大小设置为多少？
                read_data = socket_to_read[0].recv(self.__read_buffer_size)

                socket_to_write[0].send(read_data)
            except (ConnectionAbortedError, ConnectionResetError):
                # 读取客户端输入时，客户端可能直接断开连接了
                print('===========================================')
                print('[ERROR] read data from {} to {} failed'.format(socket_to_read[1], socket_to_write[1]))
                print('[ERROR] remote host may be reset the connection.')
                print('===========================================')
                # 由于一方已经关闭连接，另一方也主动断开连接
                socket_to_write[0].close()
                break
