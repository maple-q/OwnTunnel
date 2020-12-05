# /usr/bin/env python
# coding: utf-8
from constant.constant import Constant


class Log(object):
    def __init__(self, log_opened=False):
        self.__log_opened = log_opened

        # 设置终端打印[INFO]时的颜色
        self.__INFO_MSG = '\033[1;36;40mINFO\033[0m'
        self.__WARN_MSG = '\033[1;33;40mWARN\033[0m'
        self.__ERROR_MSG = '\033[1;31;40mERROR\022[0m'

    def log_optional(self, level, msg):
        """
        如果开启了打印详细日志的选项，才打印
        :param level: 日志等级
        :param msg: 需要打印的字符串
        :return:
        """
        if self.__log_opened:
            print('[{}] {}'.format(level, msg))

    def log(self, level, msg):
        """
        正常打印
        :param level: 日志等级
        :param msg: 需要打印的字符串
        :return:
        """
        if level == Constant.INFO:
            print('[{}] {}'.format(self.__INFO_MSG, msg))
        elif level == Constant.WARN:
            print('[{}] {}'.format(self.__WARN_MSG, msg))
        elif level == Constant.ERROR:
            print('[{}] {}'.format(self.__ERROR_MSG, msg))
