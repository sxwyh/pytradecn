#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：执行日志记录
# 建立日期：2023.8.24
# 联系方式：谁的谁（41715399@qq.com）
#
# 开源软件声明：
# 本软件遵守“MIT License”开源协议开源，仅供学习和参考。您可以自由使用或修改源代码或二进制文件，但必须保留上述版权声明。
# 该软件旨在深度学习和挖掘python pywinauto库的功能和潜力，由于环境的不确定性和该软件的不可靠性，请不要将该软件应用于
# 实盘交易。如您确需量化交易实盘功能，请使用券商提供的量化交易平台，否则由于您使用该软件实盘交易所造成的账户损失或政策风
# 险，开源软件提供者或插件提供者均不承担任何责任。同时，无论是直接的、间接的、偶然的、潜在的因使用该软件所造成的账号安全
# 损失、数据安全损失、账户资产损失或其他任何责任事故，开源软件提供者或插件提供者均不承担任何责任。请不要将该软件应用于商
# 业活动，否则由于把该软件应用于商业活动所造成的一切损失或法律责任，开源软件提供者或插件提供者均不承担任何责任。
#
# 修改日志：
#   2023-08-24  第一次编写
#

import logging
import warnings

from time import strftime, localtime
from os.path import join


class Logger(object):

    def __init__(self):
        self.__logger = logging.getLogger(__package__)
        self.__addstreamhandler()

    def __addstreamhandler(self):
        formatter = logging.Formatter(fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)

        self.__logger.addHandler(sh)

    def addfilehandler(self, path):
        formatter = logging.Formatter(fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        file = join(path, strftime('%Y-%m-%d', localtime()) + '.log')

        fh = logging.FileHandler(file, 'a')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        self.__logger.addHandler(fh)

    def __set_level(self, level):
        self.__logger.setLevel(level)

    def reset(self):
        self.disable()

    def disable(self):
        self.__set_level(logging.WARNING)

    def enable(self):
        self.__set_level(logging.DEBUG)

    def debug(self, msg):
        self.__logger.debug(msg)

    def info(self, msg):
        self.__logger.info(msg)

    def warning(self, msg):
        self.__logger.warning(msg)

    def warn(self, msg):
        warnings.warn(msg)
        return self

    def error(self, msg):
        self.__logger.error(msg)

    def exception(self, msg):
        self.__logger.exception(msg)

    def critical(self, msg):
        self.__logger.critical(msg)


logger = Logger()
logger.disable()
