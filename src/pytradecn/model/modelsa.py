#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：各种交易模型
# 建立日期：2023.08.29
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
#   2022-08-29  第一次编写
#

import re

from .basemodel import BaseModel
from ..logger import logger
from ..error import StockCodeError, StockPriceError, StockCountError, TradeFailFError


class DefaultModel(BaseModel):
    """默认交易模型"""

    name = 'DEFAULT'

    def __init__(self, client):
        super(DefaultModel, self).__init__(client)

    def __product_menu_select(self, item):
        """选择产品"""
        self._get_control(self._client.PRODUCT_MENU_ID).select(item)

    def __left_menu_select(self, menu, item):
        """左侧树形菜单功能选择"""
        self._get_control(menu).get_item(item).select()

    def __product_item_select(self, product, item):
        """同时选择产品和功能"""
        self._get_control(self._client.PRODUCT_MENU_ID).select(product).get_item(item).select()

    def __verify_stock_code(self, code):
        """检查证券代码"""
        if re.match(r'^\d{6}$', code) is None:
            raise StockCodeError('证券代码必须为6位数字')

        self._get_control(self._client.STOCK_CODE_ID).set_text(code)

    def __verify_stock_price(self, price):
        """
        检查价格是否正确，此方法并没有对价格的最小单位进行限制
        """
        # 价格为空时，默认当前买入卖出价
        if price is None or price == '':
            return

        # 没有对小数点后的位数进行限制
        if re.match(r'^(([1-9]\d*)|0)(\.\d*)?$', str(price)) is None:
            raise StockPriceError('价格必须为规范的数字型')

        self._get_control(self._client.STOCK_PRICE_ID).set_text(str(price))

    def __verify_stock_count(self, count):
        """
        检查买卖数量是否正确，此方法并没有对数量是否满足手（或张）的倍数进行验证
        """
        if count is None or re.match(r'^[1-9]\d*$', str(count)) is None:
            raise StockCountError('买卖数量必须为规范的数字型或不为0')

        self._get_control(self._client.STOCK_COUNT_ID).set_text(str(count))

    def __verify_stock_trade(self):
        """验证交易是否正确"""
        pane = self._prompt.tooltip(title=self._client.ENTRUST_CONFIRMBOX_TITLE)
        if pane is not None:
            pane.ok()

        pane = self._prompt.tooltip(title=self._client.ENTRUST_PROMPTBOX_TITLE)
        if pane is not None:
            content = pane.content()
            pane.close()
            mat = re.match(self._client.ENTRUST_SUCCESS_CONTENT, content)
            if mat is not None:
                return mat.group(self._client.ENTRUST_SUCCESS_SERIALINDEX)  # 成功则返回合同编号
            else:
                raise TradeFailFError(content)

        logger.warn('捕捉不到委托合同编号，可能客户端关闭了委托成功提示框')
        return ''

    def __trade(self, code='', price=None, count=None):
        # 买入和卖出共享一个下单界面
        self.__verify_stock_code(code)  # 证券代码
        self.__verify_stock_price(price)  # 买卖价格
        self.__verify_stock_count(count)  # 买卖数量
        # 买入/卖出
        self._prompt.close()  # 关闭可能存在的弹出框
        self._get_control(self._client.STOCK_TRADE_ID).click()
        return self.__verify_stock_trade()

    def initialization(self):
        """初始化交易窗口，暂不支持精简模式"""
        if self._prompt.exists(text=self._client.LOGIN_LOCKED_TEXT):
            # 客户端被锁屏
            pane = self._prompt.tooltip(text=self._client.LOGIN_LOCKED_TEXT)
            pane.child(self._client.LOGIN_LOCKPASSWORD_ID).set_text(self._client.psw)
            pane.ok()

        if self._prompt.exists(text=self._client.LOGIN_UNLINK_TEXT):
            # 客户端长时间闲置，连接被断开
            self._prompt.tooltip(text=self._client.LOGIN_UNLINK_TEXT).ok()

        # 关闭其他弹窗
        self._prompt.close()

    def reset(self):
        """复位交易窗口的功能"""
        # 复位至股票买入
        # self.__product_item_select(self._client.PRODUCT_STOCK_INDEX, [self._client.LEFTMENU_STOCK_BUY])
        pass

    def buy(self, code='', price=None, count=None, **kwargs):
        """执行买入操作"""
        self.__product_item_select(self._client.PRODUCT_STOCK_INDEX, [self._client.LEFTMENU_STOCK_BUY])
        return self.__trade(code=code, price=price, count=count)

    def sell(self, code='', price=None, count=None, **kwargs):
        """执行卖出操作"""
        self.__product_item_select(self._client.PRODUCT_STOCK_INDEX, [self._client.LEFTMENU_STOCK_SELL])
        return self.__trade(code=code, price=price, count=count)  # 买入卖出使用一个下单界面

    def cancel(self, **kwargs):
        """执行撤单操作"""
        self.__product_item_select(self._client.PRODUCT_STOCK_INDEX, [self._client.LEFTMENU_STOCK_CANCEL])

        rtn = []
        for item in self._get_control(self._client.GRID_DEFAULT_ID).refresh().items(**kwargs):
            item.select()
            rtn.append(item)

        if rtn:
            # 关闭可能存在的弹出框
            self._prompt.close()
            # 点击撤单按钮, 不需要等待撤单按钮可用，底层已有等待机制 .wait('enabled')
            self._get_control(self._client.CANCLE_SUBMIT_ID).click()
            # 弹出确认对话框
            pane = self._prompt.tooltip(text=self._client.ENTRUST_CANCELPROMPT_TITLE)  # 设置正确的参数
            if pane is not None:
                pane.ok()
            # 关闭可能的提示对话框
            self._prompt.start_monitor(delay=1.5)

        return rtn

    def query(self, target, **kwargs):
        self.__product_item_select(self._client.PRODUCT_STOCK_INDEX, [self._client.LEFTMENU_STOCK_QUERY, target])
        return self._get_control(self._client.GRID_DEFAULT_ID).refresh()
