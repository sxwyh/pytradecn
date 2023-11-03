#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：各种客户端定义
# 建立日期：2023.07.15
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
#   2022-07-15  第一次编写
#

from os.path import dirname, join
from .baseclient import BaseClient


class YH(BaseClient):
    """银河证券客户端"""
    # 账号信息
    user = '123456'   # 资金账号，目前只支持资金账号登录
    psw = '123456'   # 密码

    # 客户端安装位置
    path = join(dirname(__file__), r'银河证券\xiadan.exe')

    # 客户端信息
    version = '5.0'
    name = '银河双子星'
    key = 'yh'

    # 客户端登录窗口和交易窗口规范,只要能区别即可，没必要都填写（除control_count外），使用inspect.exe查看，参数如下：
    # title：            有这个标题的窗口，inspect.exe下的name属性
    # title_re：         标题与此正则表达式匹配的窗口
    # class_name：       具有此窗口类的窗口
    # class_name_re：    类与此正则表达式匹配的窗口
    # control_type：     具有此控件类型的窗口
    # auto_id：          具有此自动化ID的窗口
    # control_count:     该窗口在无任何弹窗时的子项数，*必填项*
    loginwindow = dict(title='用户登录', control_count=20)
    tradewindow = dict(title='网上股票交易系统5.0', control_count=4)

    # 登录引擎名
    loginengine = 'VERIFYCODEPLUS'
