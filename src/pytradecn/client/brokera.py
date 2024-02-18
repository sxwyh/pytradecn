#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：内置客户端
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

# from .baseclient import BaseClient
#
#
# class YH(BaseClient):
#     """银河客户端"""
#
#     # 以下为固定参数，不跟随交易模板、登录引擎、交易模型的改变而不同
#     # 账号信息
#     user = '123456'  # 资金账号、客户号、上A股东、深A股东等
#     psw = '654321'  # 第一密码
#     second = None  # 第二密码:通讯密码、认证口令、ukey口令等，没有时请设置为None
#     account = {}  # 账户中的其他自定义信息
#
#     # 客户端安装位置，大小写敏感，且盘符为大写，如：D:\weituo\银河证券\xiadan.exe
#     # 如果path为空，pytradecn将根据客户端信息name的设置自动查找，大部分同花顺下的独立下单程序均能找到
#     # 少数不行，为避免查找时间，建议您正确设置该参数
#     # path = r'D:\Program Files\weituo\银河证券\xiadan.exe'
#     path = ''
#
#     # 客户端信息
#     version = '5.0'
#     name = '银河证券'
#     key = 'yh'  # 客户端设别符，重要关键参数，一定保持唯一
#
#     # 客户端登录窗口和交易主窗口规范,只要能区别即可，没必要都填写（除control_count外），使用inspect.exe查看，参数如下：
#     # title：            有这个标题的窗口，inspect.exe下的name属性
#     # title_re：         标题与此正则表达式匹配的窗口
#     # class_name：       具有此窗口类的窗口
#     # class_name_re：    类与此正则表达式匹配的窗口
#     # control_type：     具有此控件类型的窗口
#     # auto_id：          具有此自动化ID的窗口
#     # control_count:     该窗口在无任何弹窗时的子项数，*必填项*
#     loginwindow = dict(title='用户登录', control_count=20)
#     mainwindow = dict(title='网上股票交易系统5.0', control_count=4)
#
#     # 登录引擎名，默认DEFAULT VERIFYCODE VERIFYCODEPLUS三种登录引擎无法满足要求时，应自定义登录引擎
#     loginengine = 'VERIFYCODE'
#     # 交易模型名，默认DEFAULT模型无法满足功能要求时，应自定义模型
#     trademodel = 'DEFAULT'
#
#     # 设置交易的速度模式，注意：会影响同时操作的所有客户端
#     TRADE_SPEED_MODE = 'fast'  # turbo（极速）、fast（快速）、defaults(默认)、slow（慢速）、dull（极慢）
#
#     # 提示框弹出框相关
#     PROMPT_TITLE_ID = '1365'
#     PROMPT_CONTENT_ID = '1004'
#     PROMPT_OKBUTTON_TITLE = '(确定|是|现在测评|我知道了|保存|立即升级).*'
#     PROMPT_CANCELBUTTON_TITLE = '(取消|否|稍后测评|我知道了|以后再说).*'
#     PROMPT_CLOSE_BUTTON = ('1008', '1003')  # 关闭按钮可能有不同的id
