# /usr/bin/env python
# coding: utf-8
from Crypto.Cipher import AES
from constant.constant import Constant


class AESCrypto(object):
    def __init__(self, key, init_vector=None, mode=Constant.MODE_CBC):
        """
        初始化
        :param key: 加密密钥
        :param init_vector: 初始化向量
        :param mode: AES加密方式，默认为CBC
        """
        self.__init_vector_length = 16
        if mode == Constant.MODE_CBC and init_vector is None:
            # CBC如果不传递初始化向量，则生成16位全位0的向量
            init_vector = '0' * 16

        self.__init_vector = init_vector

        # TODO 实例化加密算法，这里不能实例化，CBC模式下上一次加解密后影响下一次的加解密
        if mode != Constant.MODE_CBC and mode != Constant.MODE_ECB:
            raise Exception("Unsupported AES mode: {}".format(mode))

        self.__mode = mode

        # AES块大小
        self.__block_size = 16
        # 判断key长度
        if len(key) != self.__block_size:
            raise Exception('The length of key must be {}!'.format(self.__block_size))

        self.__key = key

    def __get_cipher(self):
        """
        获取加解密对象
        :return:
        """
        if self.__mode == Constant.MODE_CBC:
            return AES.new(self.__key, AES.MODE_CBC, self.__init_vector)
        elif self.__mode == Constant.MODE_ECB:
            return AES.new(self.__key, AES.MODE_ECB)

    def encrypt(self, data):
        """
        AES加密
        :param data:
        :return:
        """
        # 先进行填充，再加密
        data = self.fill(data, self.__block_size)

        # 实例化加密对象
        cipher = self.__get_cipher()
        return cipher.encrypt(data)

    def decrypt(self, data):
        """
        AES解密
        :param data:
        :return:
        """
        if not data:
            raise Exception('AES Decrypt Error: data length is zero.')
        # 先判断是否是16的倍数，AES加密后必然是16的倍数
        if len(data) % self.__block_size != 0:
            raise Exception('AES Decrypt Error: invalid AES data!')

        # 去掉填充的字符
        cipher = self.__get_cipher()
        return self.remove_filled_data(cipher.decrypt(data))

    @staticmethod
    def fill(data, block_size):
        """
        PKCS7 Padding填充
        :param data:
        :param block_size:
        :return:
        """
        # 计算需要填充的字符串长度
        length = block_size - len(data) % block_size
        data = data + ''.join([chr(length) for _ in range(length)])

        return data

    def remove_filled_data(self, data):
        """
        去除掉PKCS7 Padding填充的字符
        :param data:
        :return:
        """
        length = ord(data[-1])

        return data[:-length]
