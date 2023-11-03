#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：各种交易模板
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
    模板用来定义功能，但不实现功能。功能的实现应该由模型（model）来完成。有4个功能必须完成定义，因为这4个功能在模板基类中被定义
    这4个功能分别是buy（买入）、sell（卖出）、cancel（撤单）、query（查询）。任何定义的功能都必须添加@BaseTemplate.connect
    修饰器才能正常工作。
"""

from .basetemplate import BaseTemplate


class DefaultTemplate(BaseTemplate):

    name = 'DEFAULT'

    def __init__(self, client):
        super(DefaultTemplate, self).__init__(client)

    @BaseTemplate.connect
    def buy(self, code='', price=None, count=None, **kwargs):
        return self._model.buy(code=code, price=price, count=count)

    @BaseTemplate.connect
    def sell(self, code='', price=None, count=None, **kwargs):
        return self._model.sell(code=code, price=price, count=count)

    @BaseTemplate.connect
    def cancel(self, **kwargs):
        return self._model.cancel(**kwargs)

    @BaseTemplate.connect
    def query(self, target, **kwargs):
        return self._model.query(target)
