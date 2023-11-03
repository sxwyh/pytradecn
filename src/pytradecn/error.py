#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：错误模板
# 建立日期：2023.8.03
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
#   2023-08-03  第一次编写

from pywinauto.timings import TimeoutError


TimeOutError = TimeoutError


class ElementAmbiguousError(Exception):
    """找到多个元素"""
    pass


class ElementNotFoundError(Exception):
    """找不到元素"""
    pass


class ItemKeyError(Exception):
    """表格字段错误"""
    pass


class ClientConfigError(Exception):
    """客户端配置错误"""
    pass


class TradeFailFError(Exception):
    """交易失败错误"""
    pass


class StockCountError(Exception):
    """证券数量错误"""
    pass


class StockPriceError(Exception):
    """证券价格错误"""
    pass


class StockCodeError(Exception):
    """证券代码错误"""
    pass


class ScreenLockedError(Exception):
    """电脑屏幕被锁定"""
    pass


class LoginError(Exception):
    """登录错误"""
    pass


class RecordNotFoundError(Exception):
    """没有找到表格中的记录"""
    pass


class RecordAmbiguousError(Exception):
    """找到表格中多条记录"""
    pass
