#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：设计总体架构的模板规划
# 建立日期：2023.08.20
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
#   2022-08-20  第一次编写
#
"""
    模板就象是汽车的总装车间，模板基类用来完成交易模板的基础行为，模板只用来定义功能而不实现功能，功能的实现应有交易模型（model）完成。
"""

from abc import ABCMeta, abstractmethod
from functools import wraps

from pywinauto.timings import Timings
from pywinauto.application import AppStartError

from ..client.baseclient import BaseClientMeta
from ..prompt import PromptManager
from ..engine.baseengine import BaseEngine
from ..model.basemodel import BaseModel
from ..logger import logger
from ..error import ClientConfigError, TimeoutError


class BaseTemplateMeta(ABCMeta):
    """交易模板元类"""

    templates = {}

    def __init__(cls, name, bases, attrs):

        super(BaseTemplateMeta, cls).__init__(name, bases, attrs)

        if name != 'BaseTemplate':
            BaseTemplateMeta.templates[attrs['name']] = cls

    def __call__(cls, client=None, user=None, psw=None, second=None, **account):
        client = BaseClientMeta.clients[-1] if client is None else client
        client.user = user if user is not None else client.user
        client.psw = psw if psw is not None else client.psw
        client.second = second if second is not None else client.second
        client.account.update(account)
        return super(BaseTemplateMeta, cls).__call__(client)


class BaseTemplate(metaclass=BaseTemplateMeta):
    """
    交易模板的基类，有4个功能在其子类中必须有定义，分别是buy（买入）、sell（卖出）、cancel（撤单）、query（查询），任何在子类中定义
    的功能都必须添加@BaseTemplate.connect修饰器才能正常工作。在子类中self._client用于访问客户端，self._prompt用于访问弹窗管理
    器，模板基类是唯一对外接口，外部访问时使用Trader()访问，下面是在您的项目中的访问方法：

    """

    name = ''  # 交易模板的名称

    def __new__(cls, client):
        return object.__new__(BaseTemplateMeta.templates[client.tradetemplate])

    def __init__(self, client):
        self._client = client
        self._prompt = PromptManager(client)
        getattr(Timings, client.TRADE_SPEED_MODE)()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # if exc_type is not None:
        #    logger.error(''.join(traceback.format_exception(exc_type, exc_val, exc_tb)))
        self.close()

    def close(self):
        self._prompt.stop_monitor()
        self._client.close()

    def __login(self):
        if self._client.window() is self._client.loginwindow:
            # 用户未登录
            BaseEngine(self._client).login()
            self._client.tradewindow.wait('ready', timeout=15)  # 等待交易主窗口准备好
            self._prompt.start_monitor(delay=5)  # 关闭自动弹出的提示框
            BaseModel.model_object.pop(self._client.key, None)  # 建立新对象
            self._model = BaseModel(self._client)
        else:
            # 用户已登录
            self._model = BaseModel(self._client)
            self._model.initialization()  # 初始化交易窗口

        self._model.reset()

    def __hook(self):
        self._client.hook()

    def __active(self):
        self._client.active()

    def __setapp(self):
        try:
            self._client.connect()
        except (AppStartError, TimeoutError):
            raise ClientConfigError(f'无法启动客户端，可能路径拼写错误：{self._client.path}')

    def __unlock(self):
        """软件的自动化依赖电脑在登录的情况下"""
        # if win32gui.GetForegroundWindow() == 0:
        #    raise ScreenLockedError('屏幕被锁定')  # 操作系统限制，无法用软件解锁电脑
        # return self
        pass

    def __connect(self):
        # 1.电脑屏幕是否被锁定
        self.__unlock()
        # 2.启动应用程序
        self.__setapp()
        # 3.激活应用程序
        self.__active()
        # 4.调用钩子
        self.__hook()
        # 5.登录应用程序
        self.__login()

    @staticmethod
    def connect(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                self.__connect()
                return True, func(self, *args, **kwargs)
            except Exception as err:
                logger.exception(str(err))
                return False, str(err)
        return wrapper

    @abstractmethod
    def buy(self, code='', price=None, count=None, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def sell(self, code='', price=None, count=None, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def cancel(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def query(self, target, **kwargs):
        raise NotImplementedError()


Template = BaseTemplate
