#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：各种自定义控件
# 建立日期：2023.07.20
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
#   2022-07-20  第一次编写
#

from os import remove
from csv import DictReader
from decimal import Decimal
from tempfile import NamedTemporaryFile
from os.path import exists

from .baseuiawrapper import BaseUIAWrapper
from ..error import RecordNotFoundError, RecordAmbiguousError, ItemKeyError, TimeoutError


class PromptWrapper(BaseUIAWrapper):

    _control_types = ['Prompt']

    def __init__(self, elem):
        super(PromptWrapper, self).__init__(elem)

    def __wait_prompt_close(self):
        try:
            # NOTE 使用_get_control从顶层窗口查找
            self._get_control({'handle': self.handle}).wait_not('exists')
        except TimeoutError:
            # 超时因存在关闭确认框或其他已知的原因
            pass

    @property
    def title(self):
        title_spec = self.child(self._client.PROMPT_TITLE_ID)
        return title_spec.window_text() if title_spec.exists() else ''

    def content(self):
        text_spec = self.child(self._client.PROMPT_CONTENT_ID)
        return text_spec.window_text() if text_spec.exists() else ''

    def ok(self):
        ok_btn = self.child({
            'title_re': self._client.PROMPT_OKBUTTON_TITLE,
            'control_type': 'Button'
        })
        if ok_btn.exists():
            ok_btn.click()
            self.__wait_prompt_close()

    def cancel(self):
        cancel_btn = self.child({
            'title_re': self._client.PROMPT_CANCELBUTTON_TITLE,
            'control_type': 'Button'
        })
        if cancel_btn.exists():
            cancel_btn.click()
            self.__wait_prompt_close()

    def close(self):
        # FIXME 有弹框关闭时会弹出确认对话框
        criterias = list(self._client.PROMPT_CLOSE_BUTTON)
        criterias.extend([
            {'title_re': self._client.PROMPT_CANCELBUTTON_TITLE, 'control_type': 'Button'},
            {'title_re': self._client.PROMPT_OKBUTTON_TITLE, 'control_type': 'Button'}
        ])

        for criteria in criterias:
            cls_btn = self.child(criteria)
            if cls_btn.exists():  # 非捕捉模式
                cls_btn.click()
                self.__wait_prompt_close()
                break


class GridItem(object):
    """表格中的项，非控件"""

    def __init__(self, grid, data):
        self.__grid = grid
        self.__data = data

        config = self.__grid.config
        self.__headHeight = 24 if config('headHeight') is None else config('headHeight')
        self.__lineHeight = 24 if config('lineHeight') is None else config('lineHeight')
        self.__offset = 6 if config('offset') is None else config('offset')

    def __getitem__(self, item):
        try:
            return self.__data[item]
        except KeyError:
            raise ItemKeyError(f'表格中没有<{item}>字段')

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __str__(self):
        return str(self.__data)

    def __repr__(self):
        return str(self.__data)

    def __getattribute__(self, attr):
        return object.__getattribute__(self, attr)

    def __getattr__(self, item):
        if item not in ['pop', 'popitem', 'update', 'setdefault', 'clear', 'fromkeys']:
            return getattr(self.__data, item)
        else:
            raise AttributeError(f'GridItem对象没有{item}属性')

    def click(self, x=None, double=False):
        self.__grid.click_input(
            coords=(x, self.__headHeight + int(self.__lineHeight >> 1) + (self.__lineHeight * self.__data['index'])),
            double=double
        )

    def double_click(self):
        self.click(double=True)

    def select(self):
        self.click(x=self.__offset)


class GridWrapper(BaseUIAWrapper):

    _control_types = ['GridCSV']

    def __init__(self, elem):
        super(GridWrapper, self).__init__(elem)

    def __getitem__(self, item):
        return self.__data[item]

    def __getattribute__(self, attr):
        return object.__getattribute__(self, attr)

    def __getattr__(self, item):
        if item in ['count', 'index', 'copy']:
            return getattr(self.__data, item)
        else:
            raise AttributeError(f'GridWrapper对象没有{item}属性')

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
        # saveto.child(self.config('savetofile')).set_text(file)
        savetofile = saveto.child(self.config('savetofile'))
        # 将鼠标移动到输入框，否则微软UIA的接口会找不到主窗口，不知何故
        savetofile.click_input()
        savetofile.set_text(file)
        saveto.ok()

    def __save_csv_and_parse(self):
        """使用另存为方式保存数据"""
        with NamedTemporaryFile(mode='w+', prefix='WYH_', suffix='.csv', newline='', delete=True) as f:
            file = f.name

        self.__saveto(file)
        while not exists(file):  # 等待保存完成
            pass

        with open(file, newline='') as csvfile:
            reader = DictReader(csvfile)
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
