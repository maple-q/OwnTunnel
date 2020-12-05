#! /usr/bin/python
# coding: utf-8


class Constant(object):
    # 套接字未初始化状态
    SOCKET_NOT_INIT = 0
    # 套接字关闭状态
    SOCKET_CLOSE = -1
    # 套接字监听状态
    SOCKET_STARTING = 1

    # 日志等级
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'

    # AES加密方式，暂支持CBC和ECB模式
    MODE_CBC = 'CBC'
    MODE_ECB = 'ECB'
