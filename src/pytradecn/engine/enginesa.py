#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：各种登录引擎
# 建立日期：2023.08.16
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
#   2022-08-16  第一次编写
#

from .baseengine import BaseEngine
from ..error import LoginError, TimeoutError


class VerifyCodeEngine(BaseEngine):

    name = 'VERIFYCODE'

    def __init__(self, client):
        super(VerifyCodeEngine, self).__init__(client)

    def login(self):

        for i in range(self._client.LOGIN_MAX_TIMES):
            self._prompt.close()  # 关闭可能存在的提示框或登录失败后的提示框
            self._get_control(self._client.LOGIN_USER_ID).set_text(self._client.user)  # 资金账号
            self._get_control(self._client.LOGIN_PASSWORD_ID).set_text(self._client.psw)  # 交易密码
            if self._client.second is not None:
                self._get_control(self._client.LOGIN_SECOND_ID).set_text(self._client.second)  # 第二密码
            self._get_control(self._client.LOGIN_VERIFYCODE_ID).set_text(
                self._get_control(self._client.LOGIN_VERIFYCODEIMAGE_ID).window_text()
            )  # 验证码
            self._get_control(self._client.LOGIN_SUBMIT_ID).click()  # 登录按钮
            try:
                self._client.loginwindow.wait_not('exists', timeout=self._client.LOGIN_MAX_WAIT)
                break  # 登录成功退出循环
            except TimeoutError:
                continue  # 登录不成功
        else:
            # 达到最大登录次数，登录不成功
            self._prompt.close()  # 关闭可能存在的登录错误提示框
            raise LoginError('登录不成功！')  # 登录不成功


class VerifyCodePlusEngine(BaseEngine):

    name = 'VERIFYCODEPLUS'

    def __init__(self, client):
        super(VerifyCodePlusEngine, self).__init__(client)

    def login(self):

        for i in range(self._client.LOGIN_MAX_TIMES):
            self._prompt.close()  # 关闭可能存在的提示框或登录失败后的提示框
            self._get_control(self._client.LOGIN_USER_ID).set_text(self._client.user)  # 资金账号
            self._get_control(self._client.LOGIN_PASSWORD_ID).set_text(self._client.psw)  # 交易密码
            if self._client.second is not None:
                self._get_control(self._client.LOGIN_SECOND_ID).set_text(self._client.second)  # 第二密码
            self._get_control(self._client.LOGIN_VERIFYCODE_ID).set_text(
                self._get_control(self._client.LOGIN_VERIFYCODEIMAGE_ID).refresh().window_text()
            )  # 验证码
            self._get_control(self._client.LOGIN_SUBMIT_ID).click()  # 登录按钮
            try:
                self._client.loginwindow.wait_not('exists', timeout=self._client.LOGIN_MAX_WAIT)
                break  # 登录成功退出循环
            except TimeoutError:
                continue  # 登录不成功
        else:
            # 达到最大登录次数，登录不成功
            self._prompt.close()  # 关闭可能存在的登录错误提示框
            raise LoginError('登录不成功！')  # 登录不成功


class DefaultEngine(BaseEngine):

    name = 'DEFAULT'

    def __init__(self, client):
        super(DefaultEngine, self).__init__(client)

    def login(self):

        for i in range(self._client.LOGIN_MAX_TIMES):
            self._prompt.close()  # 关闭可能存在的提示框或登录失败后的提示框
            self._get_control(self._client.LOGIN_USER_ID).set_text(self._client.user)  # 资金账号
            self._get_control(self._client.LOGIN_PASSWORD_ID).set_text(self._client.psw)  # 交易密码
            if self._client.second is not None:
                self._get_control(self._client.LOGIN_SECOND_ID).set_text(self._client.second)  # 第二密码
            self._get_control(self._client.LOGIN_SUBMIT_ID).click()  # 登录按钮
            try:
                self._client.loginwindow.wait_not('exists', timeout=self._client.LOGIN_MAX_WAIT)
                break  # 登录成功退出循环
            except TimeoutError:
                continue  # 登录不成功
        else:
            # 达到最大登录次数，登录不成功
            self._prompt.close()  # 关闭可能存在的登录错误提示框
            raise LoginError('登录不成功！')  # 登录不成功
