#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：UIA控件规范
# 建立日期：2023.08.05
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
#   2023-08-05  第一次编写
#

import re

from pywinauto import win32structures
from pywinauto.application import WindowSpecification
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.findbestmatch import MatchError
from pywinauto.controls import InvalidWindowHandle, InvalidElement
from pywinauto.timings import Timings, wait_until, wait_until_passes, TimeoutError

from .error import ClientConfigError, ElementAmbiguousError, ElementNotFoundError

win32structure = win32structures


def find_elements(class_name=None,
                  class_name_re=None,
                  parent=None,
                  title=None,
                  title_re=None,
                  visible_only=True,
                  enabled_only=True,  # 默认为Ture
                  # best_match=None,  # 此场景没什么用
                  handle=None,
                  ctrl_index=None,
                  found_index=None,
                  predicate_func=None,
                  # active_only=False,  # 此场景无用
                  control_id=None,
                  control_type=None,
                  auto_id=None,
                  framework_id=None,
                  depth=None,
                  # 自定义参数
                  control_key=None,
                  control_define=None,
                  top_parent=None,
                  **config
                  ):
    """查找元素"""
    elements = parent.descendants(class_name=class_name,
                                  control_type=control_type,
                                  cache_enable=True,
                                  depth=depth
                                  )

    # 按顺序过滤，最大可能减少循环次数
    if ctrl_index is not None:
        elements = elements[ctrl_index:ctrl_index+1] if len(elements) > ctrl_index else []

    if handle is not None and elements:  # 不用采用官方的方法
        elements = [elem for elem in elements if elem.handle == handle]

    if auto_id is not None and elements:
        elements = [elem for elem in elements if elem.automation_id == auto_id]

    if control_id is not None and elements:
        elements = [elem for elem in elements if elem.control_id == control_id]

    if framework_id is not None and elements:
        elements = [elem for elem in elements if elem.framework_id == framework_id]

    if title is not None and elements:
        # TODO: some magic is happenning here
        elements = [elem for elem in elements if elem.rich_text == title]
    elif title_re is not None and elements:
        title_regex = re.compile(title_re)

        def _title_match(w):
            """Match a window title to the regexp"""
            t = w.rich_text
            if t is not None:
                return title_regex.match(t)
            return False

        elements = [elem for elem in elements if _title_match(elem)]

    # if class_name is not None and elements:
    #     elements = [elem for elem in elements if elem.class_name == class_name]

    if class_name_re is not None and elements:
        class_name_regex = re.compile(class_name_re)
        elements = [elem for elem in elements if class_name_regex.match(elem.class_name)]

    if visible_only and elements:
        elements = [elem for elem in elements if elem.visible]

    if enabled_only and elements:
        elements = [elem for elem in elements if elem.enabled]

    # 倒数第二个过滤条件
    if predicate_func is not None and elements:
        elements = [elem for elem in elements if predicate_func(elem)]

    # 最后一个过滤条件
    if found_index is not None:
        elements = elements[found_index:found_index+1] if len(elements) > found_index else []

    # 设置自定义参数
    for ele in elements:
        ele.control_key = control_key or ele.control_type  # control_key if control_key isnot None else ele.control_type
        ele.control_define = control_define
        ele.top_parent = top_parent
        ele.current_parent = parent
        ele.config = config

    return elements


class UIAControlSpecification(object):

    def __init__(self, criteria):

        self.__criteria = criteria

        self.__wait_criteria_map = {
            'exists': ('exists',),
            'visible': ('is_visible',),
            'enabled': ('is_enabled',),
            'ready': ('is_visible', 'is_enabled',),
            'active': ('is_active',),
        }

    def __getattribute__(self, attr):
        return object.__getattribute__(self, attr)

    def __getattr__(self, attr):
        return getattr(self.wrapper_object(), attr)

    def __get_ctrl(self):

        elements = find_elements(**self.__criteria)

        if not elements:
            raise ElementNotFoundError('找不到控件:{0}'.format(self.__criteria['control_define']))

        if len(elements) > 1:
            exception = ElementAmbiguousError('找到{0}个控件，在此条件下:{1}'.format(
                len(elements),
                str(self.__criteria['control_define']),
            ))
            exception.elements = elements
            raise exception

        return UIAWrapper(elements[0])

    def __resolve_control(self, timeout=None, retry_interval=None):

        # 不要设置为默认值
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        try:
            return wait_until_passes(
                timeout,
                retry_interval,
                self.__get_ctrl,
                (ElementNotFoundError, ElementAmbiguousError, MatchError, InvalidWindowHandle, InvalidElement)
                )
        except TimeoutError as err:
            raise ClientConfigError(str(err.original_exception))

    def wrapper_object(self):
        return self.__resolve_control()

    def exists(self, timeout=None, retry_interval=None):
        """判断控件是否存在，默认非捕捉模式"""

        # 不要设置为默认值，时间会更改
        if timeout is None:
            # timeout = Timings.exists_timeout
            timeout = 0
        if retry_interval is None:
            retry_interval = Timings.exists_retry

        # 默认值visible_only=True, enabled_only=True, 官方关闭这两个参数主要针对窗口且有其普遍道理
        # 不用关闭这两个参数，盈余规范参数保持一致
        # visible_only = self.__criteria.get('visible_only', True)
        # enabled_only = self.__criteria.get('enabled_only', True)
        #
        # self.__criteria['visible_only'] = False
        # self.__criteria['enabled_only'] = False

        try:
            self.__resolve_control(timeout, retry_interval)
            # self.__criteria['visible_only'] = visible_only
            # self.__criteria['enabled_only'] = enabled_only
            return True
        except ClientConfigError:  # 这里跟__resolve_control抛出的错误一致
            # self.__criteria['visible_only'] = visible_only
            # self.__criteria['enabled_only'] = enabled_only
            return False

    def __parse_wait_args(self, wait_conditions, timeout, retry_interval):

        # 解析等待条件，直接使用官方代码
        if timeout is None:
            timeout = Timings.window_find_timeout
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        # 转换成小写
        wait_for = wait_conditions.lower()

        # 集合具有去重功能
        unique_check_names = set()
        # 将字符串解析成列表
        wait_criteria_names = wait_for.split()
        # 遍历等待列表
        for criteria_name in wait_criteria_names:
            try:
                # 从映射表中获得方法元组
                check_methods = self.__wait_criteria_map[criteria_name]
            except KeyError:
                # Invalid check name in the wait_for
                raise SyntaxError('意外的条件 - %s' % criteria_name)
            else:
                # 将方法元组添加到集合中，注：集合会解包元组，并去掉重复项
                unique_check_names.update(check_methods)

        # 最终的unique_check_names如下：
        # unique_check_names = set(['is_enabled', 'is_active', 'is_visible', 'Exists'])
        return unique_check_names, timeout, retry_interval

    def __check_all_conditions(self, check_names, retry_interval):

        # 检查所有的条件，直接使用官方代码

        # 遍历所有的检查方法
        for check_name in check_names:
            # timeout = retry_interval because the timeout is handled at higher level
            if check_name == 'exists':  # 如果是exists()
                check = getattr(self, check_name)
                if not check(retry_interval, float(retry_interval) // 2):
                    return False  # 不成功，直接返回False
                else:
                    continue  # 成功则检查下一个条件
            try:
                # 获得控件包装器
                ctrl = self.__resolve_control(retry_interval, float(retry_interval) // 2)
                check = getattr(ctrl, check_name)  # 获得方法
            except ClientConfigError:  # 这里跟__resolve_control抛出的错误一致
                # 控件不存在，直接返回False. 所以'enabled', 'active', 'visible', 'ready'会同时检查控件是否存在
                return False
            else:
                if not check():
                    # 条件不满足，直接返回False
                    return False
            # 满足条件，继续循环下一个判断

        # 所有的条件均满足，返回True
        return True

    def wait(self, wait_for, timeout=None, retry_interval=None):
        # 直接使用官方代码
        check_method_names, timeout, retry_interval = self.__parse_wait_args(wait_for, timeout, retry_interval)
        wait_until(timeout, retry_interval,
                   lambda: self.__check_all_conditions(check_method_names, retry_interval))

        # 返回控件包装器
        return self.wrapper_object()

    def wait_not(self, wait_for_not, timeout=None, retry_interval=None):
        # 直接使用官方代码
        check_method_names, timeout, retry_interval = self.__parse_wait_args(wait_for_not, timeout, retry_interval)
        wait_until(timeout, retry_interval,
                   lambda: not self.__check_all_conditions(check_method_names, retry_interval))


def str2dict(control_str: str) -> dict:

    criteria = {}

    args = control_str.split('|')
    # 1.设置found_index参数
    criteria['found_index'] = None if len(args) < 4 or args[3] == '' else int(args[3])
    # 2.设置predicate_func参数，以实现控件设别
    criteria['control_key'] = None if len(args) < 3 or args[2] == '' else args[2]
    # 3.设置control_type参数
    criteria['control_type'] = None if len(args) < 2 or args[1] == '' else args[1]
    # 4.设置auto_id参数，字符串始终有一个
    criteria['auto_id'] = None if args[0] == '' else args[0]

    return criteria


def criteria_parser(control_define: (str, dict)) -> dict:

    if isinstance(control_define, str):
        criteria = str2dict(control_define)
    elif isinstance(control_define, dict) and 'control' in control_define:
        criteria = str2dict(control_define['control'])
        criteria.update(control_define)
        criteria.pop('control', None)
    else:
        criteria = control_define.copy()

    criteria['control_define'] = control_define

    return criteria


def get_control_specification(parent, control_define, top_parent=None):
    # 必须包含parent参数
    if isinstance(parent, (WindowSpecification, UIAControlSpecification, UIAWrapper)):
        parent = parent.element_info

    if top_parent is not None:
        if isinstance(top_parent, (WindowSpecification, UIAControlSpecification, UIAWrapper)):
            top_parent = top_parent.element_info
    else:
        top_parent = parent

    criteria = criteria_parser(control_define)
    criteria['parent'] = parent
    criteria['top_parent'] = top_parent

    return UIAControlSpecification(criteria)
