#
# 同花顺客户端自动化实现插件
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 插件功能：实现同花顺客户端的登录、交易
# 建立日期：2023.10.20
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
#   2022-10-20  第一次编写
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
from os import remove
from csv import DictReader
from decimal import Decimal
from tempfile import NamedTemporaryFile
from os.path import exists

from pytradecn.client.baseclient import BaseClient
from pytradecn.template.basetemplate import BaseTemplate
from pytradecn.engine.baseengine import BaseEngine
from pytradecn.model.basemodel import BaseModel
from pytradecn.control.baseuiawrapper import BaseUIAWrapper
from pytradecn.control.wrappersa import GridItem

from pytradecn.logger import logger
from pytradecn.error import StockCodeError, StockPriceError, StockCountError, TradeFailFError
from pytradecn.error import RecordNotFoundError, RecordAmbiguousError, LoginError, TimeoutError


class THS92030(BaseClient):
    """同花顺客户端9.20.30，由于其内嵌在同花顺行情软件中，最好手动启动并登录同花顺行情软件并从行情软件打开客户端"""

    # 以下为固定参数，不跟随交易模板、登录引擎、交易模型的改变而不同
    # 账号信息
    user = '123456'  # 资金账号、客户号、上A股东、深A股东等
    psw = '654321'  # 第一密码
    second = None  # 第二密码:通讯密码、认证口令、ukey口令等，没有时请设置为None
    account = {}  # 账户中的其他自定义信息

    # 客户端安装位置，大小写敏感，且盘符为大写，如：D:\weituo\银河证券\xiadan.exe
    path = r'D:\Users\Administrator\xiadan.exe'

    # 客户端信息
    version = '9.20.30'
    name = '同花顺'
    key = 'ths92030'  # 客户端设别符，重要关键参数，一定保持唯一

    # 客户端登录窗口和交易窗口规范,只要能区别即可，没必要都填写（除control_count外），使用inspect.exe查看，参数如下：
    # title：            有这个标题的窗口，inspect.exe下的name属性
    # title_re：         标题与此正则表达式匹配的窗口
    # class_name：       具有此窗口类的窗口
    # class_name_re：    类与此正则表达式匹配的窗口
    # control_type：     具有此控件类型的窗口
    # auto_id：          具有此自动化ID的窗口
    # control_count:     该窗口在无任何弹窗时的子项数，*必填项*
    loginwindow = dict(title='', control_type='Pane', control_count=16)
    tradewindow = dict(title='网上股票交易系统5.0', control_type='Window', control_count=4)

    # 交易模板名,默认DEFAULT模板无法满足功能要求时，应自定义模板
    tradetemplate = 'THS_9_20_30'
    # 登录引擎名，默认DEFAULT VERIFYCODE VERIFYCODEPLUS三种登录引擎无法满足要求时，应自定义登录引擎
    loginengine = 'THS_9_20_30'
    # 交易模型名，默认DEFAULT模型无法满足功能要求时，应自定义模型
    trademodel = 'THS_9_20_30'

    # 设置交易的速度模式，注意：会影响同时操作的所有客户端
    TRADE_SPEED_MODE = 'fast'  # defaults(默认速度)、slow（慢速）、fast（快速）
    # 提示框弹出框相关
    PROMPT_TITLE_ID = '1365'
    PROMPT_CONTENT_ID = '1004'
    PROMPT_OKBUTTON_TITLE = '(确定|是|现在测评|我知道了|保存|立即升级).*'
    PROMPT_CANCELBUTTON_TITLE = '(取消|否|稍后测评|我知道了|以后再说).*'
    PROMPT_CLOSE_BUTTON = ('1008', '1003')  # 关闭按钮可能有不同的id

    # 结尾为 “_ID” 的参数表示控件的设别规范，完整的control_id如下：
    # control_id = 'auto_id|control_type|control_key|found_index',
    # 其中control_key为控件标识符，control_key不存在时，默认为control_type
    # auto_id，control_type，find_index应至少存在一个，应保证找到唯一控件
    # 该控件如有其他参数，采用字典形式传入

    # 控件参数和设置参数跟随交易模板、登录引擎、交易模型的不同而不同
    # 登录引擎THS_9_20_30所需要的控件规范和设置参数
    # 登录相关控件
    LOGIN_USER_ID = '1001|Edit|Editor'
    LOGIN_PASSWORD_ID = '1012|Edit|Editor'
    LOGIN_SECOND_ID = '1012|Edit|Editor'
    LOGIN_VERIFYCODE_ID = '1003|Edit|Editor'
    # 验证码图像，格式固定字典 (验证码ID，验证码显示在原图像的位置box（left, upper, right, lower），白名单whitelist，刷新按钮refresh)
    # 默认值，box=None,大小为原图像；whitelist=None，白名单为空；refresh=None刷新按钮为验证码图像本身
    LOGIN_VERIFYCODEIMAGE_ID = {
        'control': '1499|Image|Verifycode',
        'box': (None, None, None, None),
        'whitelist': '0123456789',
        'refresh': None
    }
    # 登录按钮
    LOGIN_SUBMIT_ID = '1006'
    # 登录的最大试错次数
    LOGIN_MAX_TIMES = 5
    # 每次登录的间隔时间（秒），此参数也用来判断登录是否成功，电脑性能差运行速度慢时，将此参数调高
    LOGIN_MAX_WAIT = 7

    # 交易模型THS_9_20_30所需要的设置参数和控件规范
    # 锁屏密码框的文本，长时间不用会被锁屏
    LOGIN_LOCKED_TEXT = '请输入您的交易密码'
    # 锁屏密码框的密码输入框
    LOGIN_LOCKPASSWORD_ID = '1039|Edit|Editor'
    # 客户端被断开连接的文本，长时间不用与服务器的连接会被断开
    LOGIN_UNLINK_TEXT = '您的请求.+已超时，可能网络忙'
    # 产品菜单
    PRODUCT_MENU_ID = {
        'control': '1001|Pane|Tabpane',
        'tabs': [
            {'name': '股票交易', 'rect': (1, 2, 72, 20), 'link': '129|Tree'},
            {'name': '开放式基金(场外)', 'rect': (73, 2, 174, 20), 'link': '240|Tree'},
            {'name': '银河理财', 'rect': (175, 2, 244, 20), 'link': '909|Tree'},
            {'name': '证券出借', 'rect': (1, 21, 62, 39), 'link': '2037|Tree'},
            {'name': '账户管理', 'rect': (63, 21, 134, 39), 'link': '830|Tree'},
        ]
    }
    PRODUCT_STOCK_INDEX = 0
    PRODUCT_FUND_INDEX = 1
    PRODUCT_MONEY_INDEX = 2
    PRODUCT_LEND_INDEX = 3
    PRODUCT_ACCOUNT_INDEX = 4

    # 左侧股票交易树形菜单
    LEFTMENU_STOCK_ID = '129|Tree'
    LEFTMENU_STOCK_BUY = '买入[F1]'
    LEFTMENU_STOCK_SELL = '卖出[F2]'
    LEFTMENU_STOCK_CANCEL = '撤单[F3]'
    LEFTMENU_STOCK_QUERY = '查询[F4]'

    # 左侧开放式基金树形菜单
    # 默认无此功能，可自行添加

    # 股票交易界面，买入卖出使用同一下单界面
    STOCK_CODE_ID = '1032|Edit|Editor'
    STOCK_PRICE_ID = '1033|Edit|Editor'
    STOCK_COUNT_ID = '1034|Edit|Editor'
    STOCK_TRADE_ID = '1006'
    # 委托买卖确认框标题，支持正则表达式
    ENTRUST_CONFIRMBOX_TITLE = '委托确认'
    # 委托买卖提示框标题，支持正则表达式
    ENTRUST_PROMPTBOX_TITLE = r'提示.*'
    # 委托买卖成功后的提示内容信息正则
    ENTRUST_SUCCESS_CONTENT = r'您的(买入|卖出)委托已成功提交，合同编号：(\d+)。'
    # 委托买卖成功后，“合同编号”位于上述表达式中的组号
    ENTRUST_SUCCESS_SERIALINDEX = 2

    # 表格相关
    GRID_DEFAULT_ID = {
        'control': '1047|Pane|THSGridCSV|1',
        'headHeight': 20,
        'lineHeight': 17,
        'offset': 8,
        'saveto': '|Window|Prompt',
        'savetofile': '1001|Edit'
    }
    GRID_VERIFYCODE_TEXT = '检测到您正在保存数据，为保护您的账号数据安全，请'
    GRID_VERIFYCODE_ID = '2404|Edit|Editor'
    GRID_VERIFYCODEIMAGE_ID = {
        'control': '2405|Image|Verifycode',
        'box': (None, None, None, None),
        'whitelist': '0123456789',
        'refresh': None
    }

    # 撤单界面
    CANCLE_SUBMIT_ID = '1099'
    # 委托撤单确认框内容，支持正则表达式
    ENTRUST_CANCELPROMPT_TITLE = '撤单确认'


class THS92030Engine(BaseEngine):
    """同花顺验证码登录引擎"""

    name = 'THS_9_20_30'

    def __init__(self, client):
        super(THS92030Engine, self).__init__(client)

    def login(self):
        for i in range(self._client.LOGIN_MAX_TIMES):
            self._prompt.close()  # 关闭可能存在的提示框或登录失败后的提示框
            self._get_control(self._client.LOGIN_USER_ID).set_text(self._client.user)  # 资金账号
            self._get_control(self._client.LOGIN_PASSWORD_ID).set_text(self._client.psw)  # 交易密码
            if self._client.second is not None:
                self._get_control(self._client.LOGIN_SECOND_ID).set_text(self._client.second)  # 第二密码
            if self._get_control(self._client.LOGIN_VERIFYCODEIMAGE_ID).exists():
                self._get_control(self._client.LOGIN_VERIFYCODE_ID).set_text(
                    self._get_control(self._client.LOGIN_VERIFYCODEIMAGE_ID).window_text()
                    # self._get_control(self._client.LOGIN_VERIFYCODEIMAGE_ID).refresh().window_text()  # 刷新
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


class THS92030Template(BaseTemplate):
    """同花顺模板，模板只用来定义功能，但不实现功能，功能的实现由模型完成"""

    name = 'THS_9_20_30'

    def __init__(self, client):
        super(THS92030Template, self).__init__(client)

    @BaseTemplate.connect
    def buy(self, code='', price=None, count=None, **kwargs):
        return self._model.buy(code=code, price=price, count=count)

    @BaseTemplate.connect
    def sell(self, code='', price=None, count=None, **kwargs):
        return self._model.sell(code=code, price=price, count=count)

    @BaseTemplate.connect
    def cancel(self, **kwargs):
        return self._model.cancel(**kwargs)

    @BaseTemplate.connect
    def query(self, target, **kwargs):
        return self._model.query(target)

    # 在这里添加其他功能
    @BaseTemplate.connect
    def test(self):
        return '测试'


class THS92030tModel(BaseModel):
    """同花顺的交易模型，用来完成模板中定义功能的具体实现"""

    name = 'THS_9_20_30'

    def __init__(self, client):
        super(THS92030tModel, self).__init__(client)

    # def __product_menu_select(self, item):
    #     """选择产品"""
    #     self._get_control(self._client.PRODUCT_MENU_ID).select(item)
    #
    # def __left_menu_select(self, menu, item):
    #     """左侧树形菜单功能选择"""
    #     self._get_control(menu).get_item(item).select()

    def __product_item_select(self, product, item):
        """同时选择产品和功能"""
        self._get_control(self._client.PRODUCT_MENU_ID).select(product).get_item(item).select()

    def __verify_stock_code(self, code):
        """检查证券代码，此方法没有对证券代码是否存在进行验证"""
        if re.match(r'^\d{6}$', code) is None:
            raise StockCodeError('证券代码必须为6位数字')

        self._get_control(self._client.STOCK_CODE_ID).set_text(code)

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

        self._get_control(self._client.STOCK_PRICE_ID).set_text(str(price))

    def __verify_stock_count(self, count):
        """
        检查买卖数量是否正确，此方法并没有对数量是否满足手（或张）的倍数进行验证
        没有对买卖数量是否超出最大限额进行验证，可以自行补充
        """
        if count is None or re.match(r'^[1-9]\d*$', str(count)) is None:
            raise StockCountError('买卖数量必须为规范的数字型或不为0')

        self._get_control(self._client.STOCK_COUNT_ID).set_text(str(count))

    def __verify_stock_trade(self):
        """
        验证交易是否正确
        注意：此方法没有多市场标的的选择功能，没有ST股票的确认功能
        """
        pane = self._prompt.tooltip(title='提示信息')
        if pane is not None:
            pane.ok()

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
        """初始化交易窗口，暂不支持精简模式，必须存在此方法"""
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
        """复位交易窗口的功能，必须存在此方法"""
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
        """
        执行撤单操作
        注意：无法判断委托单是否已选中，可能会造成撤单错误。如果已选中，再select一次会变成未选中，造成撤单错误
        使用方法参考后面表格控件的items()方法
        """
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
            self._prompt.start_monitor(delay=1)

        return rtn

    def query(self, target, **kwargs):
        """查询功能没有日期选择功能，可以自行补充"""
        self.__product_item_select(self._client.PRODUCT_STOCK_INDEX, [self._client.LEFTMENU_STOCK_QUERY, target])
        return self._get_control(self._client.GRID_DEFAULT_ID).refresh()


class THSGridWrapper(BaseUIAWrapper):
    """为同花顺客户端定制的表格控件，因其保存时会弹出验证码"""

    _control_types = ['THSGridCSV']

    def __init__(self, elem):
        super(THSGridWrapper, self).__init__(elem)

    def __getitem__(self, item):
        return self.__data[item]

    def __getattribute__(self, attr):
        return object.__getattribute__(self, attr)

    def __getattr__(self, item):
        if item in ['count', 'index', 'copy']:
            return getattr(self.__data, item)
        else:
            raise AttributeError(f'THSGridWrapper对象没有{item}属性')

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __repr__(self):
        rtn = '['
        for item in self.__data:
            rtn += '\n\t' + str(item) + ','
        return rtn + '\n]'

    def __str__(self):
        rtn = '['
        for item in self.__data:
            rtn += '\n\t' + str(item) + ','
        return rtn + '\n]'

    def __saveto(self, file):
        # 关闭可能存在的弹窗
        self._prompt.close()
        self.set_focus().type_keys('^s')

        saveto = self._get_control(self.config('saveto'))

        # 捕捉是否有验证码提示框
        pane = self._prompt.tooltip(text=self._client.GRID_VERIFYCODE_TEXT)
        if pane is not None:
            # 由于提示框tooltip的捕捉机制以及弹窗的等待关闭机制，故exists()不需要捕捉模式
            while not saveto.exists():  # 默认非捕捉模式
                pane.child(self._client.GRID_VERIFYCODE_ID).set_text(
                    # 选择是否主动刷新验证码
                    # pane.child(self._client.GRID_VERIFYCODEIMAGE_ID).refresh().window_text()
                    pane.child(self._client.GRID_VERIFYCODEIMAGE_ID).window_text()
                )
                # 由于点击确认后，验证码提示框并不会主动关闭，故判断“另存为”对话框是否弹出作为验证码是否正确的判断依据
                pane.ok()

        # 这里感觉“卡”一下，是因为虽然“另存为”对话框已弹出，但弹窗的“等待关闭”机制仍在等待验证码提示框关闭，但验证码提示框不关闭
        saveto.child(self.config('savetofile')).set_text(file)
        saveto.ok()

    def __save_csv_and_parse(self):
        """使用另存为方式保存数据"""
        with NamedTemporaryFile(mode='w+', prefix='WYH_', suffix='.csv', newline='', delete=True) as f:
            file = f.name

        self.__saveto(file)
        while not exists(file):  # 等待保存完成
            pass

        with open(file, newline='') as csvfile:
            reader = DictReader(csvfile, dialect='excel-tab')  # 同花顺表格采用excel-tab变种
            self.__data = [GridItem(self, dict(index=reader.line_num-2, **row)) for row in reader]  # row为何是str？

        if exists(file):
            remove(file)

    def items(self, **kwargs):
        """
        依据给定的条件过滤列表，返回过滤后的列表（行，即GridItem对象）

        kwargs关键字可以是表格标头的任何一个字段，value是一个字符串或由字符串组成的元组，
        即使像成交价格、成交数量等在GridWrapper中仍然以字符串格式保存，这样做的好处是
        便于使用Decimal类进行浮点数运算，而不会因计算机浮点数危机使价格计算错误。

        items()方法是GridWrapper对象的核心方法，使用场景可能如下：

        1、获得全部委托单
        grid.items()
        2、使用一个关键字参数过滤列表
        grid.items(证券名称='农业银行')  # 所有证券名称为‘农业银行’的委托单
        3、使用多个关键字参数过滤列表
        grid.items(证券名称='农业银行', 操作='买入')  # 将农业银行的买入单过滤出来
        4、使用一个关键字参数，多值过滤列表
        grid.items(证券名称=('农业银行', '平安银行'))  # 所有证券名称为‘农业银行’和‘平安银行’的委托单
        grid.items(合同编号=('123456', '654321'))  # 合同编号为‘123456’和‘654321’的委托单
        5、使用多关键字参数，多值过滤列表
        grid.items(证券名称=('农业银行', '平安银行'), 操作='买入')  # 农业银行和平安银行的买入单
        """
        table = self.__data.copy()
        for key, value in kwargs.items():
            values = (str(value),) if isinstance(value, (str, int, float, Decimal)) else value
            table = [row for row in table if row[key] in values]
        return table

    def item(self, **kwargs):
        """依据给定的条件，返回一个匹配的项目"""
        table = self.items(**kwargs)

        if not table:
            raise RecordNotFoundError(kwargs)

        if len(table) > 1:
            exception = RecordAmbiguousError('有{0}条记录, 在此条件下{1}'.format(len(table), str(kwargs),))
            exception.table = table
            raise exception

        return table[0]

    def refresh(self):
        self.type_keys('{F5}')
        # FIXME 等待刷新完成？self是否还有效？
        self.__save_csv_and_parse()
        return self
