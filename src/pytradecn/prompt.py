#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：管理各类弹窗和提示窗
# 建立日期：2022.12.01
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
#   2022-12-01  第一次编写
#   2024-08-09  添加自定义属性，与uiacontrol.py保持一致
#   2024-08-28  解决有些客户端弹窗与主窗口处于同一级的问题
#

import re
import operator
import time

from threading import Thread
from pywinauto.timings import wait_until_passes, TimeoutError, Timings
from pywinauto.findbestmatch import find_best_control_matches

from .control.wrappersa import PromptWrapper


class PromptManagerMeta(type):

    def __init__(cls, name, bases, attrs):
        super(PromptManagerMeta, cls).__init__(name, bases, attrs)

    def __call__(cls, client):
        if client.prompt is None:
            client.prompt = super(PromptManagerMeta, cls).__call__(client)
        return client.prompt


class PromptManager(metaclass=PromptManagerMeta):
    """
    弹窗或提示窗管理器，可以对弹窗进行存在性判断、关闭或捕捉提示框。
    管理弹窗时，不应该将此类实例化，而是使用登录引擎基类或模型基类中提供的_prompt属性。
    即使您将此类实例化，您实例化的对象也与_prompt属性指向用一个对象（单例模式）。
    """

    def __init__(self, client):
        self.__client = client
        self.__monitorthread = None
        self.__monitorrun = False

    def __get_prompts(self):
        """获得所有弹窗"""
        window = self.__client.window()
        child_count = window.child_count  # 似乎以计数的方法更为可靠
        prompt_level = window.prompt_level

        # 获得弹窗的父项，有一些弹窗与窗口处于同一级别
        parent = window.element_info  # 需要返回元素，而非包装器
        while prompt_level < 0:
            parent = parent.parent
            prompt_level = prompt_level + 1

        # 获取所有弹窗
        elements = parent.children(process=self.__client.app.process)[:-child_count]

        if elements:
            elements = [elem for elem in elements if elem.process_id == self.__client.app.process]

        if elements:
            elements = [elem for elem in elements if elem.control_type in self.__client.PROMPT_TYPE_LIST]

        if elements:
            elements = [elem for elem in elements if len(elem.children(process=elem.process_id)) > 0]

        # 与uiacontrol.py保持一致
        for elem in elements:
            elem.control_key = 'Prompt'  # 与 PromptWrapper类中的_control_types属性一致
            elem.control_define = {
                'class_name': elem.class_name,
                'title': elem.rich_text,
                'handle': elem.handle,
                'control_type': elem.control_type,
                'auto_id': elem.automation_id,
                'process': elem.process_id
            }
            elem.current_parent = elem.parent
            elem.config = {}

        # 返回弹窗包装器
        return [PromptWrapper(ele) for ele in elements]

    def __find_prompts(self,
                       title=None,       # 对话框标题，支持正则表达式
                       content=None,     # 对话框内容
                       text=None,        # **对话框中的所有inspect.exe可见文字字符串，支持正则表达式，这是一个万能参数**
                       best_match=None,  # pywinauto的参数，可以用但作用不大
                       func=None,        # 定义一个函数去筛选
                       ):
        """依据给定的条件，筛选符合条件的对话框"""

        panes = self.__get_prompts()

        if title is not None and panes:
            panes = [pane for pane in panes if re.match(title, pane.title)]

        if content is not None and panes:
            panes = [pane for pane in panes if re.match(content, pane.content())]

        if text is not None and panes:
            panes = [pane for pane in panes if list(filter(lambda x: re.match(text, x), pane.texts()))]

        if best_match is not None and panes:
            panes = find_best_control_matches(best_match, panes)

        if func is not None and panes:
            panes = [pane for pane in panes if func(pane)]

        return panes

    def __monitor(self, duration, kwargs):
        """监视弹窗并关闭"""
        start = time.perf_counter()

        while self.__monitorrun is True:
            for pane in self.__find_prompts(**kwargs):
                pane.close()

            time_left = duration - (time.perf_counter() - start)

            if time_left > 0:
                time.sleep(min(Timings.window_find_retry, time_left))
            else:
                self.__monitorrun = False

    def stop_monitor(self):
        if self.__monitorthread is not None and self.__monitorthread.is_alive():
            self.__monitorrun = False
            self.__monitorthread.join()

    def start_monitor(self, delay=0, **kwargs):
        self.stop_monitor()
        self.__monitorrun = True
        self.__monitorthread = Thread(target=self.__monitor, name='PromptClose', args=(delay, kwargs))
        self.__monitorthread.start()

    def close(self, **kwargs):
        """关闭当前所有存在的弹窗"""
        self.stop_monitor()
        for pane in self.__find_prompts(**kwargs):
            pane.close()

    def tooltip(self, timeout=None, retry_interval=None, **kwargs):
        """提示框应用场景，采用捕捉模式"""
        self.stop_monitor()
        # 不要设置为默认值
        if timeout is None:
            timeout = Timings.window_find_timeout * 0.6
        if retry_interval is None:
            retry_interval = Timings.window_find_retry

        try:
            return wait_until_passes(timeout,
                                     retry_interval,
                                     operator.getitem,
                                     (IndexError,),
                                     self.__find_prompts(**kwargs),
                                     0  # 总是返回最上面的提示框
                                     )
        except TimeoutError:
            return None

    def exists(self, timeout=None, retry_interval=None, **kwargs):
        """判断弹窗是否存在，默认非捕捉模式"""
        # 不要设置为默认值，时间会更改
        if timeout is None:
            # timeout = Timings.exists_timeout
            timeout = 0
        if retry_interval is None:
            retry_interval = Timings.exists_retry

        return self.tooltip(timeout, retry_interval, **kwargs) is not None
