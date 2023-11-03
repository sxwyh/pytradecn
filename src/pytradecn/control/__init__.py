#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：UIA控件库
# 建立日期：2023.08.18
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

from pywinauto.base_wrapper import BaseWrapper
from pywinauto.controls.uiawrapper import UiaMeta, UIAWrapper

from . import wrappersa, wrappersb, wrappersc  # 导入模块以注册模块中的控件


# 重写UIAWrapper.find_wrapper方法以支持识别自定义控件
def get_wrapper(element):
    """Find the correct wrapper for this UIA element"""
    # Set a general wrapper by default
    wrapper_match = UIAWrapper

    # Check for a more specific wrapper in the registry
    # if element.control_type in UiaMeta.control_type_to_cls:
    #    wrapper_match = UiaMeta.control_type_to_cls[element.control_type]

    # Check for a more specific wrapper in the registry
    try:
        if element.control_key in UiaMeta.control_type_to_cls:
            wrapper_match = UiaMeta.control_type_to_cls[element.control_key]
    except AttributeError:  # 没有control_key属性
        if element.control_type in UiaMeta.control_type_to_cls:
            wrapper_match = UiaMeta.control_type_to_cls[element.control_type]

    return wrapper_match


UIAWrapper.find_wrapper = get_wrapper


# 重写BaseWrapper._create_wrapper方法以解决控件被两次初始化的BUG，官方版本0.6.8
def build_wrapper(cls_spec, element_info, myself):
    """Create a wrapper object according to the specified element info"""
    # only use the meta class to find the wrapper for BaseWrapper
    # so allow users to force the wrapper if they want

    if cls_spec != myself:
        obj = object.__new__(cls_spec)
        # obj.__init__(element_info)
        return obj

    new_class = cls_spec.find_wrapper(element_info)
    obj = object.__new__(new_class)
    # obj.__init__(element_info)
    return obj


BaseWrapper._create_wrapper = build_wrapper


# def criteria_parser(control_define):
#     """控件规范解析器"""
#     # control_define = 'auto_id|control_type|control_key|found_index'
#     # FIXME None时不要传参
#
#     criteria = {'enabled_only': True}  # 应用场景要求元素可用
#     args = control_define['control'].split('|') if isinstance(control_define, dict) else control_define.split('|')
#
#     # 1.设置found_index参数
#     criteria['found_index'] = None if len(args) < 4 or args[3] == '' else int(args[3])
#     # 2.设置predicate_func参数，以实现控件设别
#     control_key = None if len(args) < 3 or args[2] == '' else args[2]
#
#     def predicate_func(ele):
#         ele.control_key = control_key if control_key is not None else ele.control_type
#         ele.element_define = control_define
#         return True
#
#     criteria['predicate_func'] = predicate_func
#
#     # 3.设置control_type参数
#     criteria['control_type'] = None if len(args) < 2 or args[1] == '' else args[1]
#     # 4.设置auto_id参数，字符串始终有一个
#     criteria['auto_id'] = None if args[0] == '' else args[0]
#
#     return criteria


# UIAWrapper.criteria_parser = criteria_parser
