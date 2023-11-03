#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：设计自定义UIA控件基类
# 建立日期：2023.09.28
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
#   2023-09-28  第一次编写
#

from ..client import get_client
from ..utils.ocr import image_to_string
from ..uiacontrol import UIAWrapper, win32structure, get_control_specification


class BaseUIAWrapper(UIAWrapper):

    _control_types = ['BaseUIA']

    def __init__(self, element_info):
        super(BaseUIAWrapper, self).__init__(element_info)
        self._client = get_client(process=element_info.process_id)
        self._prompt = self._client.prompt
        self._win32structure = win32structure

    def _get_control(self, control_define):
        # control_define 为Client格式的字符串或字典，或者pywinauto格式的字典
        return get_control_specification(self._client.window(), control_define)

    def config(self, key):  # 弹出框无法使用
        return self.element_info.config.get(key, None)

    def top_level_parent(self):
        # NOTE 官方top_level_parent()效率低且易出错，重写
        # return self._client.window().wrapper_object()  # 注意：集成环境下仍然指向客户端主窗口
        return self._client.root_window().wrapper_object()

    def standard(self):
        """返回此控件的pywinauto官方标准控件"""
        # NOTE 不要在条件中添加type和class，有可能失效
        return get_control_specification(self.element_info.parent, {'handle': self.element_info.handle})

    def own(self):  # 弹出框无法使用
        """返回此控件的另一个副本"""
        return get_control_specification(self.element_info.current_parent, self.element_info.control_define)

    def child(self, control_define):
        """返回此控件的后代规范"""
        # control_define 为Client格式的字符串或字典，或者pywinauto格式的字典
        return get_control_specification(self.element_info, control_define)

    def texts(self):
        """重写texts()"""
        rtn = [c.window_text() for c in self.descendants() if c.window_text() != '']
        return [self.window_text()] + list(map(lambda s: s.replace('\r', '').replace('\n', ''), rtn))

    def image_text(self, box=None, whitelist=None):
        """返回控件的表面可见文本"""
        if whitelist is None:
            whitelist = ''
        return image_to_string(self.capture_as_image(box), tessedit_char_whitelist=whitelist)

    def exists(self, timeout=None):
        """判断控件是否还存在"""
        return self._get_control({'handle': self.handle}).exists(timeout=timeout)


Wrapper = BaseUIAWrapper
