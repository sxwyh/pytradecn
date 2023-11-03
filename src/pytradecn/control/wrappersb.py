#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：各种自定义控件
# 建立日期：2023.08.10
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
#   2022-08-10  第一次编写
#

from .baseuiawrapper import BaseUIAWrapper


class EditorWrapper(BaseUIAWrapper):
    """编辑器控件，实现统一接口"""

    _control_types = ['Editor']

    def __init__(self, elem):
        super(EditorWrapper, self).__init__(elem)

    def set_edit_text(self, text):
        # 直接使用self.xxx_input()等模拟鼠标键盘事件，会在UIAElementInfo()出现"COMError -2147220991, '事件无法调用任何订户'错误"
        # 原因可能与操作系统相关的权限控制有关，但pywinauto(0.6.8)不会报错，同时将所有的element属性置为None。
        # 但WindowSpecification.xxx_input()不会有问题，WindowSpecification每次操作会新建不同的包装器对象，
        # 故采用以下方法，每次使用不同的包装器跳过此问题
        self.standard().double_click_input()
        # self.standard().type_keys('{DELETE}')
        self.standard().type_keys(str(text))

        return self

    set_text = set_edit_text


class VerifycodeWrapper(BaseUIAWrapper):

    _control_types = ['Verifycode']

    def __init__(self, elem):
        """Initialize the control"""
        super(VerifycodeWrapper, self).__init__(elem)

        box = self.config('box')
        if box is not None:
            self.__box = self._win32structure.RECT()
            self.__box.left = self.rectangle().left if box[0] is None else self.rectangle().left + int(box[0])
            self.__box.top = self.rectangle().top if box[1] is None else self.rectangle().top + int(box[1])
            self.__box.right = self.rectangle().right if box[2] is None else self.rectangle().left + int(box[2])
            self.__box.bottom = self.rectangle().bottom if box[3] is None else self.rectangle().top + int(box[3])
        else:
            self.__box = self.rectangle()

        self.__whitelist = self.config('whitelist')

    def window_text(self):
        """返回Image控件的窗口文本"""
        # NOTE 这里的box相对其父元素,没有采用crop()是考虑其保存更大图像
        return self.image_text(box=self.__box, whitelist=self.__whitelist)

    def refresh(self):
        if self.config('refresh') is None:
            self.click_input(coords=(self.__box.mid_point().x - self.rectangle().left,
                                     self.__box.mid_point().y - self.rectangle().top
                                     )
                             )
        else:
            self._get_control(self.config('refresh')).click_input()

        # 验证码刷新后，原控件已失效，返回其副本
        return self.own()


class ImagedigitWrapper(BaseUIAWrapper):

    _control_types = ['Imagedigit']

    def __init__(self, elem):
        """Initialize the control"""
        super(ImagedigitWrapper, self).__init__(elem)

    def window_text(self):
        return self.image_text(whitelist='0123456789.')


class TabPaneWrapper(BaseUIAWrapper):
    """Pane类型的Tab控件"""

    _control_types = ['Tabpane']

    def __init__(self, elem):
        super(TabPaneWrapper, self).__init__(elem)

        self.__tabs = [] if self.config('tabs') is None else self.config('tabs')

    def select(self, *item):
        # 参数*item写这样，是为了让PyCharm停止警告与基类签名不匹配，不是低级错误
        # 目前只支持index
        point = self._win32structure.RECT(*self.__tabs[item[0]].get('rect')).mid_point()
        self.click_input(coords=(point.x, point.y))

        link = self.__tabs[item[0]].get('link', None)
        if link is not None:
            return self._get_control(link)
        else:
            return self

    def tab_count(self):
        return len(self.__tabs)

    def texts(self):
        return [tab['name'] for tab in self.__tabs]
