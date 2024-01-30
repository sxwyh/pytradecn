#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：设计交易模型的基础规划
# 建立日期：2023.08.29
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
#   2022-08-29  第一次编写
#

from abc import ABCMeta, abstractmethod

from ..prompt import PromptManager
from ..uiacontrol import get_control_specification


class BaseModelMeta(ABCMeta):
    """交易模型元类"""

    models = {}
    model_object = {}

    def __init__(cls, name, bases, attrs):

        super(BaseModelMeta, cls).__init__(name, bases, attrs)

        if name != 'BaseModel':
            BaseModelMeta.models[attrs['name']] = cls

    def __call__(cls, client):
        # 使用唯一标识符，key或app.process（有None风险）
        if client.key not in BaseModelMeta.model_object:
            BaseModelMeta.model_object[client.key] = super(BaseModelMeta, cls).__call__(client)
        return BaseModelMeta.model_object[client.key]


class BaseModel(metaclass=BaseModelMeta):
    """交易模型基类"""

    # 交易模型的名称
    name = ''

    def __new__(cls, client):
        return object.__new__(BaseModelMeta.models[client.trademodel])

    def __init__(self, client):
        self.__element = client.mainwindow.element_info  # 加快运行速度
        self._client = client
        self._prompt = PromptManager(client)

    def _get_control(self, control_define):
        # control_define 为Client格式的字符串或字典，或者pywinauto格式的字典
        return get_control_specification(parent=self.__element, control_define=control_define)

    @abstractmethod
    def initialization(self):
        """初始化交易窗口"""
        raise NotImplementedError()

    @abstractmethod
    def reset(self):
        """复位交易窗口的功能"""
        raise NotImplementedError()


Model = BaseModel
