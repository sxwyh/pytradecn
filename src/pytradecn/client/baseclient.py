#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：客户端基类
# 建立日期：2023.07.15
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
#   2022-07-15  第一次编写
#

from os.path import normpath

from pywinauto import Desktop
# from pywinauto.win32functions import BringWindowToTop
from pywinauto.application import Application, ProcessNotFoundError, WindowSpecification

from ..error import ClientConfigError


class BaseClientMeta(type):
    """客户端元类"""

    clients = []

    def __init__(cls, name, bases, attrs):

        super(BaseClientMeta, cls).__init__(name, bases, attrs)

        if name != 'BaseClient':

            cls.app = Application(backend="uia")

            if 'loginwindow' in attrs:
                # 主窗口设计成列表是为了兼容集成在行情软件中的交易客户端，例如通达信
                criterias_ = attrs['loginwindow']
                if isinstance(criterias_, dict):
                    criterias_ = [criterias_, ]
                criterias = [crit.copy() for crit in criterias_]
                # 对第0个元素完成处理，第0个元素是软件的界面，此时默认top_level_only=True，意味着只查找桌面的子项
                criterias[0]['app'] = cls.app
                criterias[0]['backend'] = 'uia'
                # 不需要对1以后的元素添加top_level_only、backend、parent等属性，因为pywinauto内部可以自动处理
                # 最后一个元素是真正的窗口，必须有control_count属性
                control_count = criterias[-1].pop('control_count', 20)
                # 构造真正的WindowSpecification对象
                cls.loginwindow = WindowSpecification(criterias[0])
                cls.loginwindow.criteria.extend(criterias[1:])
                # 添加自定义child_count属性，以识别弹窗
                cls.loginwindow.child_count = control_count
            else:
                raise ClientConfigError(f'客户端{cls}缺少关键配置<loginwindow>')

            if 'mainwindow' in attrs:
                # 主窗口设计成列表是为了兼容集成在行情软件中的交易客户端，例如通达信
                criterias_ = attrs['mainwindow']
                if isinstance(criterias_, dict):
                    criterias_ = [criterias_, ]
                criterias = [crit.copy() for crit in criterias_]
                # 对第0个元素完成处理，第0个元素是软件的界面，此时默认top_level_only=True，意味着只查找桌面的子项
                criterias[0]['app'] = cls.app
                criterias[0]['backend'] = 'uia'
                # 不需要对1以后的元素添加top_level_only、backend、parent等属性，因为pywinauto内部可以自动处理
                # 最后一个元素是真正的窗口，必须有control_count属性
                control_count = criterias[-1].pop('control_count', 4)
                # 构造真正的WindowSpecification对象
                cls.mainwindow = WindowSpecification(criterias[0])
                cls.mainwindow.criteria.extend(criterias[1:])
                # 添加自定义child_count属性，以识别弹窗
                cls.mainwindow.child_count = control_count
            else:
                raise ClientConfigError(f'客户端{cls}缺少关键配置<mainwindow>')

            # 最正确的做法是：cls.prompt = PromptManager(cls)，但会造成import冲突，所以在其元类中实现单例
            cls.prompt = None

            BaseClientMeta.clients.append(cls)

    # def __getattribute__(cls, attr):
    #     return object.__getattribute__(cls, attr)
    #
    # def __getattr__(cls, attr):
    #     if attr in BaseClient.__dict__:
    #         value = BaseClient.__dict__[attr]
    #         if isinstance(value, classmethod):
    #             # return lambda: rtn.__wrapped__(cls)  # 只适用于无参数时
    #             def wrapper(*args, **kwargs):
    #                 return value.__wrapped__(cls, *args, **kwargs)
    #             return wrapper
    #         else:
    #             return value
    #     else:
    #         raise ClientConfigError(f'客户端{cls}缺少名为<{attr}>的配置')


class BaseClient(metaclass=BaseClientMeta):
    """客户端的基类，不要直接使用"""

    #
    # 以下为固定参数，不跟随交易模板、登录引擎、交易模型的改变而不同
    #

    # 账号信息
    user = '123456'  # 资金账号、客户号、上A股东、深A股东等
    psw = '654321'  # 第一密码
    second = None  # 第二密码:通讯密码、认证口令、ukey口令等，没有时请设置为None
    account = {}  # 账户中的其他自定义信息

    # 客户端安装位置，大小写敏感，且盘符为大写，如：D:\weituo\银河证券\xiadan.exe
    path = ''

    # 客户端信息
    version = None
    name = None
    key = None  # 客户端设别符，重要关键参数，一定保持唯一

    # 客户端登录窗口和主窗口规范，重要参数，在具体的客户端设置
    # loginwindow = dict()
    # mainwindow = dict()

    # 交易模板名，默认DEFAULT模板无法满足功能要求时，应自定义模板
    tradetemplate = 'DEFAULT'
    # 登录引擎名，默认DEFAULT VERIFYCODE VERIFYCODEPLUS三种登录引擎无法满足要求时，应自定义登录引擎
    loginengine = 'DEFAULT'
    # 交易模型名，默认DEFAULT模型无法满足功能要求时，应自定义模型
    trademodel = 'DEFAULT'

    # 全局设置或控件参数
    # 设置交易的速度模式，注意：会影响同时操作的所有客户端
    TRADE_SPEED_MODE = 'fast'  # turbo（极速）、fast（快速）、defaults(默认)、slow（慢速）、dull（极慢）
    # 提示框弹出框相关
    PROMPT_TYPE_LIST = ('Pane', 'Window', 'Custom')
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
    # 登录引擎DEFAULT、VERIFYCODE、VERIFYCODEPLUS所需要的控件规范和设置参数
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
    LOGIN_MAX_WAIT = 6

    # 交易模型DEFAULT所需要的设置参数和控件规范
    # 锁屏密码框的文本，长时间不用会被锁屏
    LOGIN_LOCKED_TEXT = '请输入您的交易密码'
    # 锁屏密码框的密码输入框
    LOGIN_LOCKPASSWORD_ID = '1039|Edit|Editor'
    # 客户端被断开连接的文本，长时间不用与服务器的连接会被断开
    LOGIN_UNLINK_TEXT = '您的请求.+已超时，可能网络忙'
    # 产品菜单
    PRODUCT_MENU_ID = {
        'control': '1001|Pane|Tabpane',
        'class_name': 'CCustomTabCtrl',
        'tabs': [
            {'name': '股票交易', 'rect': (1, 2, 64, 19), 'link': '129|Tree'},
            {'name': '开放式基金(场外)', 'rect': (65, 2, 176, 19), 'link': '240|Tree'},
            {'name': '银河理财', 'rect': (177, 2, 240, 19), 'link': '909|Tree'},
            {'name': '证券出借', 'rect': (241, 2, 304, 19), 'link': '2037|Tree'},
            {'name': '港股通', 'rect': (1, 22, 52, 39), 'link': '5199|Tree'},
            {'name': '账户管理', 'rect': (53, 22, 116, 39), 'link': '830|Tree'},
            {'name': '柜台市场产品', 'rect': (117, 22, 204, 39), 'link': '5040|Tree'}
        ]
    }
    PRODUCT_STOCK_INDEX = 0
    PRODUCT_FUND_INDEX = 1
    PRODUCT_MONEY_INDEX = 2
    PRODUCT_LEND_INDEX = 3
    PRODUCT_HONGKONG_INDEX = 4
    PRODUCT_ACCOUNT_INDEX = 5
    PRODUCT_MARKET_INDEX = 6

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
        'control': '1047|Pane|GridCSV|1',
        'headHeight': 24,
        'lineHeight': 23,
        'offset': 6,
        'saveto': '|Window|Prompt',
        'savetofile': '1152|Edit'
    }

    # 撤单界面
    CANCLE_SUBMIT_ID = '1099'
    # 委托撤单确认框内容，支持正则表达式
    ENTRUST_CANCELPROMPT_TITLE = r'提示信息'

    #
    # 以下代码不要修改，不要修改！
    #
    # 启动真实客户端
    @classmethod
    def connect(cls):
        try:
            cls.app.connect(path=normpath(cls.path), timeout=0.6)
        except ProcessNotFoundError:
            cls.app.start(normpath(cls.path))  # app.start已内置等待机制
            # 但同花顺的下单程序集成在行情软件中，start()等待机制会失效,pywinauto会弹出警告,使用下列代码完成等待
            # NOTE 不要勾选自动登录，如需要，使用try...except...兼容自动登录
            WindowSpecification(cls.loginwindow.criteria[0]).wait("ready", timeout=15)  # 超时软件无法打开

        try:
            # 等待安静下来，对客户端的操作应该等待其上一个动作完全完成
            cls.app.wait_cpu_usage_lower(threshold=1.5, timeout=10)
        except RuntimeError:
            pass

        return cls

    @classmethod
    def window(cls):
        # 始终返回正确的主窗口，不要使用Application.top_window(),Application.active()来设置主窗口
        # 设置timeout=0，因应用场景非此即彼，并非捕捉模式，以此加快运行速度
        # 不用改变存在的判断顺序
        return cls.mainwindow if cls.mainwindow.exists(timeout=0) else cls.loginwindow

    @classmethod
    def root_window(cls):
        # 始终返回正确的根窗口，集成环境下的根窗口不是主窗口，即使集成环境下两个窗口均未打开，也能正确返回根窗口
        return WindowSpecification(cls.window().criteria[0])

    @classmethod
    def active(cls):
        # 激活客户端，NOTE：is_active()会误判
        root_window = cls.root_window()

        if root_window.is_dialog() and root_window.is_minimized():
            cls.taskbaricon().click()
        else:
            # BringWindowToTop(root_window.handle)
            root_window.set_focus()

        return cls

    @classmethod
    def taskbaricon(cls):
        # 客户端的任务栏图标按钮，未使用taskbar模块，是因为该模块仍处于实验阶段（pywinauto-0.6.8）
        # FIXME 未来使用taskbar模块
        return Desktop(backend='uia').window(class_name='Shell_TrayWnd', found_index=0).child_window(
            auto_id=normpath(cls.path),
            control_type='Button'
        )

    @classmethod
    def hook(cls):
        # 一个钩子，在激活（active）客户端后被调用，在子类重写它完成想要的功能
        # 或者实现在集成环境下打开内嵌的客户端，如下代码：
        # if not cls.window().exists(timeout=0):
        #     root_window = WindowSpecification(cls.loginwindow.criteria[0])
        #     # 此处用操作root_window打开内嵌客户端
        #     ...
        #     cls.loginwindow.wait('ready', timeout=15)

        return cls

    @classmethod
    def close(cls):
        # 关闭客户端
        try:
            cls.app.connect(path=normpath(cls.path), timeout=0.6).kill()
        except ProcessNotFoundError:
            pass


Client = BaseClient
