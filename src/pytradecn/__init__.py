#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 开源软件声明：
# 本软件遵守“MIT License”开源协议开源，仅供学习和参考。您可以自由使用或修改源代码或二进制文件，但必须保留上述版权声明。
# 该软件旨在深度学习和挖掘python pywinauto库的功能和潜力，由于环境的不确定性和该软件的不可靠性，请不要将该软件应用于
# 实盘交易。如您确需量化交易实盘功能，请使用券商提供的量化交易平台，否则由于您使用该软件实盘交易所造成的账户损失或政策风
# 险，开源软件提供者或插件提供者均不承担任何责任。同时，无论是直接的、间接的、偶然的、潜在的因使用该软件所造成的账号安全
# 损失、数据安全损失、账户资产损失或其他任何责任事故，开源软件提供者或插件提供者均不承担任何责任。请不要将该软件应用于商
# 业活动，否则由于把该软件应用于商业活动所造成的一切损失或法律责任，开源软件提供者或插件提供者均不承担任何责任。
#
# 项目软件特色：
# 该项目是始于2023年初的一个实验项目，由于个人的原因而编写，但笔者上次编写代码还是近20年前，主要使用C和汇编编写一些很底层
# 的项目。所以，该项目是笔者第一个python项目，错误在所难免。该项目通过使用python第三方库pywinauto，实现对券商客户端的
# 自动化操作测试，包括自动登录、验证码识别、买卖、撤单、查询等功能。该项目深度应用pywinauto库，代码中有许多pywinauto库
# 的应用技巧，包括该库存在的BUG也已在代码中标明。该项目具有以下特点：
# * 该项目采用一种“客户端驱动型工厂模式”设计，或者叫“客户定制式工厂模式”。所以，从理论上讲，该项目具备了支持所有券商客户端
#   及其未来版本的能力。
# * 由于交易的严谨性和严肃性，所有的操作均有返回值，要么成功要么失败，不会因运行时错误而“卡”在半路。
# * 自动化软件测试受内外环境的影响较大，该项目以最大的可能减少内外环境的变化对软件自动化的影响。
# * 由于采用“客户端驱动型工厂模式”，所以项目可扩展性高、可根据不同的券商版本制作不同的交易模型也可以制作不同的部件适应不同的
#   场景，如制作不同的登录引擎以适应不同的登录方式。
#
#
# 修改日志：
#   0.0.1   第一次编写
#   0.0.2   主窗口修改成mainwindow
#   0.0.3   email.py 中添加login模块级方法
#           添加极速极慢速模式
#   0.0.4   去掉模板选择功能，功能的定义和实现均在模型中完成
#   0.0.5   添加对Tesseract及交易客户端的自动识别，此版本存在BUG
#   0.0.6   取消内置的客户端
#   0.0.7   解决OCR路径中的空格问题
#   0.0.8   软件安装路径的标准化（资源管理器标准）
#           登录窗口和主窗口visible_only设置为False
#   0.0.9   解决部分客户端控件无handle的问题
#           客户端设置中key参数自动化
#           增强客户端path参数的自动识别
#           为窗口添加prompt_level参数，解决有些客户端弹窗与主窗口处于同一级的问题
#

import sys
from .utils import general, ocr

__version__ = '0.0.9'

# 环境检测
assert sys.platform.startswith('win'), 'pytradecn只能运行在Windows操作系统'
assert sys.version_info > (3, 9, 0), 'pytradecn只能运行在python3.9.0以上版本'

if not ocr.exists(ocr.path):
    ocr.path = ocr.join(str(general.get_app_path('Tesseract')), r'tesseract.exe')
    assert ocr.exists(ocr.path), '找不到tesseract.exe，请安装tesseract-OCR及其简体中文支持包\n' \
                                 '下载地址：https://digi.bib.uni-mannheim.de/tesseract/\n' \
                                 '语言包地址：https://github.com/tesseract-ocr/tessdata\n' \
                                 '如果您已经安装了tesseract-OCR，仍然报此错误，请使用编辑软件打开pytradecn/utils/ocr.py，设置正确的path参数'


try:
    from pywinauto.sysinfo import UIA_support
    assert UIA_support, 'pytradecn只支持UIA后端访问技术，当前设备不支持UIA访问技术'
except (ImportError, ModuleNotFoundError):
    assert False, '缺少pywinauto库，使用命令行安装：pip install pywinauto'

try:
    from PIL import Image
    from .template.basetemplate import BaseTemplate as Trader
    from .client.baseclient import BaseClient, Client
    from .engine.baseengine import BaseEngine, Engine
    from .model.basemodel import BaseModel, Model
except (ImportError, ModuleNotFoundError):
    assert False, '缺少pillow库，使用命令行安装：pip install pillow'
