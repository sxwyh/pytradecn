#
# 同花顺客户端自动化实现插件
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 插件功能：实现同花顺客户端的登录、交易
# 建立日期：2023.10.20
# 适配版本：pytradecn-0.0.4及以上
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
# 注意：同花顺客户端集成在行情软件中，如果独立启动pywinauto会弹出下面的警告，不要紧，pytradecn也能完成等待
# warnings.warn('Application is not loaded correctly (WaitForInputIdle failed)', RuntimeWarning)
#
# 修改日志：
#   2023-10-20  第一次编写
#   2024-01-29  修改为pytradecn-0.0.4格式
#
#
"""
 使用方法：
 首先修改该文件中的账号信息和客户端安装路径path
 将该文件拷贝至您项目的任意位置，如放在包 mypacket 中，在您的代码中使用如下方法调用:

 # 导入pytradecn和本插件，导入顺序不分先后
 from pytradecn import Trader
 from mypacket.ths92030 import THS92030

 trader = Trader(client=THS92030)
 print(trader.query('当日委托')[1])

 事实上，Trader方法不需要显式输入参数，pytradecn可以自动识别您定义的客户端，如下方法：
 # 导入pytradecn和本插件，导入顺序不分先后
 from pytradecn import Trader
 from mypacket.ths92030 import THS92030

 trader = Trader()  # pytradecn会自动识别您的客户端THS92030
 print(trader.query('当日委托')[1])

 或者，彻底隐藏客户端的导入，如把导入客户端放在包mypacket的__init__.py中，如下：
 # 在 mypacket.__init__.py 中
 from . import ths92030

 在您的主代码中：
 from pytradecn import Trader

 trader = Trader()  # pytradecn会自动识别您的客户端THS92030
 print(trader.query('当日委托')[1])
"""

import re

from pytradecn import BaseClient, BaseEngine, BaseModel

from pytradecn.logger import logger
from pytradecn.error import StockCodeError, StockPriceError, StockCountError, TradeFailFError
from pytradecn.error import LoginError, TimeoutError


class THS92030(BaseClient):
    """同花顺客户端9.20.30，由于其内嵌在同花顺行情软件中，最好手动启动并登录同花顺行情软件并从行情软件打开客户端"""

    # 以下为固定参数，不跟随交易模板、登录引擎、交易模型的改变而不同
    # 账号信息
    user = '123456'  # 资金账号、客户号、上A股东、深A股东等
    psw = '654321'  # 第一密码
    second = None  # 第二密码:通讯密码、认证口令、ukey口令等，没有时请设置为None
    account = {}  # 账户中的其他自定义信息

    # 客户端安装位置，大小写敏感，且盘符为大写，如：D:\weituo\银河证券\xiadan.exe
    # 如果path为空，pytradecn将根据客户端信息name的设置自动查找，大部分同花顺下的独立下单程序均能找到
    # 少数不行，为避免查找时间，建议您正确设置该参数
    # path = r'D:\Users\Administrator\xiadan.exe'
    path = ''

    # 客户端信息
    version = '9.20.30'
    name = '同花顺'
    key = 'ths92030'  # 客户端设别符，重要关键参数，一定保持唯一

    # 客户端登录窗口和交易主窗口规范,只要能区别即可，没必要都填写（除control_count外），使用inspect.exe查看，参数如下：
    # title：            有这个标题的窗口，inspect.exe下的name属性
    # title_re：         标题与此正则表达式匹配的窗口
    # class_name：       具有此窗口类的窗口
    # class_name_re：    类与此正则表达式匹配的窗口
    # control_type：     具有此控件类型的窗口
    # auto_id：          具有此自动化ID的窗口
    # control_count:     该窗口在无任何弹窗时的子项数，*必填项*
    loginwindow = {
        'title': '',
        'control_type': 'Pane',
        'predicate_func': lambda ele: ele.rectangle.height() > 35,
        'control_count': 16
    }
    mainwindow = {
        'title': '网上股票交易系统5.0',
        'control_type': 'Window',
        'predicate_func': lambda ele: ele.rectangle.height() > 35,
        'control_count': 4
    }

    # 登录引擎名，默认DEFAULT VERIFYCODE VERIFYCODEPLUS三种登录引擎无法满足要求时，应自定义登录引擎
    loginengine = 'THS_9_20_30'
    # 交易模型名，默认DEFAULT模型无法满足功能要求时，应自定义模型
    trademodel = 'THS_9_20_30'

    # 设置交易的速度模式，注意：会影响同时操作的所有客户端
    TRADE_SPEED_MODE = 'fast'  # turbo（极速）、fast（快速）、defaults(默认)、slow（慢速）、dull（极慢）

    # 提示框弹出框相关
    PROMPT_TITLE_ID = '1365'
    PROMPT_CONTENT_ID = '1004'
    PROMPT_OKBUTTON_TITLE = '(确定|是|现在测评|我知道了|保存|立即升级).*'
    PROMPT_CANCELBUTTON_TITLE = '(取消|否|稍后测评|我知道了|以后再说).*'
    PROMPT_CLOSE_BUTTON = ('1008', '1003')  # 关闭按钮可能有不同的id

    # 定义几个较复杂的控件
    LOGIN_VERIFYCODEIMAGE_ID = {
        'control': '1499|Image|Verifycode',
        'box': (None, None, None, None),
        'whitelist': '0123456789',
        'refresh': None
    }

    PRODUCT_MENU_ID = {
        'control': '1001|Pane|Tabpane',
        'class_name': 'CCustomTabCtrl',
        'tabs': [
            {'name': '股票交易', 'rect': (1, 2, 72, 20), 'link': '129|Tree'},
            {'name': '开放式基金(场外)', 'rect': (73, 2, 174, 20), 'link': '240|Tree'},
            {'name': '银河理财', 'rect': (175, 2, 244, 20), 'link': '909|Tree'},
            {'name': '证券出借', 'rect': (1, 21, 62, 39), 'link': '2037|Tree'},
            {'name': '账户管理', 'rect': (63, 21, 134, 39), 'link': '830|Tree'},
        ]
    }

    GRID_DEFAULT_ID = {
        'control': '1047|Pane|JQKGridCSV|1',
        'headHeight': 20,
        'lineHeight': 17,
        'offset': 8,
        'saveto': '|Window|Prompt',
        'savetofile': '1001|Edit',
        'verifycode_text': '检测到您正在保存数据，为保护您的账号数据安全，请',
        'verifycode_id': '2404|Edit|Editor',
        'verifycodeimage_id': {
            'control': '2405|Image|Verifycode',
            'box': (None, None, None, None),
            'whitelist': '0123456789',
            'refresh': None
        }
    }


class THS92030Engine(BaseEngine):
    """同花顺验证码登录引擎"""

    name = 'THS_9_20_30'

    def __init__(self, client):
        super(THS92030Engine, self).__init__(client)

    def login(self):
        for i in range(5):
            self._prompt.close()  # 关闭可能存在的提示框或登录失败后的提示框
            self._get_control('1001|Edit|Editor').set_text(self._client.user)  # 资金账号
            self._get_control('1012|Edit|Editor').set_text(self._client.psw)  # 交易密码
            if self._get_control('1181|Edit|Editor').exists():  # 第二密码
                self._get_control('1181|Edit|Editor').set_text(self._client.second)
            if self._get_control(self._client.LOGIN_VERIFYCODEIMAGE_ID).exists():  # 验证码
                self._get_control('1003|Edit|Editor').set_text(
                    self._get_control(self._client.LOGIN_VERIFYCODEIMAGE_ID).window_text()
                    # self._get_control(self._client.LOGIN_VERIFYCODEIMAGE_ID).refresh().window_text()  # 刷新
                )
            self._get_control('1006').click()  # 登录按钮
            try:
                self._client.loginwindow.wait_not('exists', timeout=7)  # 7秒内完成登录
                break  # 登录成功退出循环
            except TimeoutError:
                continue  # 登录不成功
        else:
            # 达到最大登录次数，登录不成功
            self._prompt.close()  # 关闭可能存在的登录错误提示框
            raise LoginError('登录不成功！')  # 登录不成功


class THS92030Model(BaseModel):
    """同花顺的交易模型"""

    name = 'THS_9_20_30'

    def __init__(self, client):
        super(THS92030Model, self).__init__(client)

    def __product_item_select(self, product, item):
        """同时选择产品和功能"""
        # 如果希望有产品选择功能
        # self._get_control(self._client.PRODUCT_MENU_ID).select(product).get_item(item).select()
        # 如果没有产品菜单
        self._get_control('129|Tree').get_item(item).select()

    def __verify_stock_code(self, code):
        """检查证券代码，此方法没有对证券代码是否存在进行验证"""
        if re.match(r'^\d{6}$', code) is None:
            raise StockCodeError('证券代码必须为6位数字')

        self._get_control('1032|Edit|Editor').set_text(code)

    def __verify_stock_price(self, price):
        """
        检查价格是否正确，此方法并没有对价格的最小单位进行限制
        没有对张跌停价进行验证，没有对价格笼子进行验证
        """
        # 价格为空时，默认当前买入卖出价
        if price is None or price == '':
            return

        # 没有对小数点后的位数进行限制
        if re.match(r'^(([1-9]\d*)|0)(\.\d*)?$', str(price)) is None:
            raise StockPriceError('价格必须为规范的数字型')

        self._get_control('1033|Edit|Editor').set_text(str(price))

    def __verify_stock_count(self, count):
        """
        检查买卖数量是否正确，此方法并没有对数量是否满足手（或张）的倍数进行验证
        没有对买卖数量是否超出最大限额进行验证，可以自行补充
        """
        if count is None or re.match(r'^[1-9]\d*$', str(count)) is None:
            raise StockCountError('买卖数量必须为规范的数字型或不为0')

        self._get_control('1034|Edit|Editor').set_text(str(count))

    def __verify_stock_trade(self):
        """
        验证交易是否正确
        注意：此方法没有多市场标的的选择功能，没有ST股票的确认功能
        """
        pane = self._prompt.tooltip(title='提示信息')
        if pane is not None:
            pane.ok()

        pane = self._prompt.tooltip(title='委托确认')
        if pane is not None:
            pane.ok()

        pane = self._prompt.tooltip(title=r'提示.*')
        if pane is not None:
            content = pane.content()
            pane.close()
            mat = re.match(r'您的(买入|卖出)委托已成功提交，合同编号：(\d+)。', content)
            if mat is not None:
                return mat.group(2)  # 成功则返回合同编号
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
        self._get_control('1006').click()
        return self.__verify_stock_trade()

    def initialization(self):
        """初始化交易窗口，暂不支持精简模式，必须存在此方法"""
        if self._prompt.exists(text='请输入您的交易密码'):
            # 客户端被锁屏
            pane = self._prompt.tooltip(text='请输入您的交易密码')
            pane.child('1039|Edit|Editor').set_text(self._client.psw)
            pane.ok()

        if self._prompt.exists(text='您的请求.+已超时，可能网络忙'):
            # 客户端长时间闲置，连接被断开
            self._prompt.tooltip(text='您的请求.+已超时，可能网络忙').ok()

        # 关闭其他弹窗
        self._prompt.close()

    def reset(self):
        """复位交易窗口的功能，必须存在此方法"""
        # 复位至股票买入
        # self.__product_item_select(0, ['买入[F1]'])
        pass

    def buy(self, code='', price=None, count=None):
        """执行买入操作"""
        self.__product_item_select(0, ['买入[F1]'])
        return self.__trade(code=code, price=price, count=count)

    def sell(self, code='', price=None, count=None):
        """执行卖出操作"""
        self.__product_item_select(0, ['卖出[F2]'])
        return self.__trade(code=code, price=price, count=count)  # 买入卖出使用一个下单界面

    def cancel(self, **kwargs):
        """
        执行撤单操作
        注意：无法判断委托单是否已选中，可能会造成撤单错误。如果已选中，再select一次会变成未选中，造成撤单错误
        使用方法参考后面表格控件的items()方法
        """
        self.__product_item_select(0, ['撤单[F3]'])

        rtn = []
        for item in self._get_control(self._client.GRID_DEFAULT_ID).refresh().items(**kwargs):
            item.select()
            rtn.append(item)

        if rtn:
            # 关闭可能存在的弹出框
            self._prompt.close()
            # 点击撤单按钮, 不需要等待撤单按钮可用，底层已有等待机制 .wait('enabled')
            self._get_control('1099').click()
            # 弹出确认对话框
            pane = self._prompt.tooltip(text='撤单确认')  # 设置正确的参数
            if pane is not None:
                pane.ok()
            # 关闭可能的提示对话框
            self._prompt.start_monitor(delay=1)

        return rtn

    def query(self, target):
        """查询功能没有日期选择功能，可以自行补充"""
        self.__product_item_select(0, ['查询[F4]', target])
        return self._get_control(self._client.GRID_DEFAULT_ID).refresh()
