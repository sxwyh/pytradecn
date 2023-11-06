#
# OCR（光学字符识别）tesseract 软件支持
# 官方网站：https://github.com/tesseract-ocr/tesseract
# 正确设置tesseract的安装路径，tesseract
#
#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：光学字符识别
# 建立日期：2023.04.12
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
#   2023-04-12  第一次编写
#   2023-11-16  添加等待保存完成
#

from os import remove
from os.path import dirname, join, exists
from tempfile import NamedTemporaryFile

from .general import command

# 正确设置tesseract的安装路径，tesseract
path = join(dirname(__file__), r'Tesseract\tesseract.exe')


def file_to_text(file='', out='stdout', psm='3', **kwargs):
    if file == '':
        raise Exception('file不能为空！')

    # if 'tessedit_char_whitelist' in kwargs and kwargs['tessedit_char_whitelist'] == '':
    #    del kwargs['tessedit_char_whitelist']

    # 构造命令行
    args = f'{path} {file} {out} -l chi_sim+eng --psm {psm} -c'
    for key in kwargs:
        args = args + f' {key}=' + kwargs[key]

    # print(args)
    return command(args)


def file_to_string(file='', out='stdout', **kwargs):
    # 因为输出字符串，所以将psm设置为7，表示单行文本
    return file_to_text(file=file, out=out, psm='7', **kwargs)


def image_to_text(im=None, out='stdout', psm='3', **kwargs):
    if im is None:
        raise Exception('image不能为空！')

    w, h = im.size
    # 将delete设置为False，以免自动删除创建的临时文件
    with NamedTemporaryFile(prefix='WYH_', suffix='.png', delete=False) as f:
        # 将图像放大一倍，转换为灰度
        im.resize((w * 2, h * 2)).convert('L').save(f, format='png')

    # 等待保存完成
    while not exists(f.name):  # 等待保存完成
        pass

    # 将代码放在with外面，因为python和tesseract不能同时打开文件
    text = file_to_text(file=f.name, out=out, psm=psm, **kwargs)
    # 手动删除创建的临时文件
    if exists(f.name):
        remove(f.name)

    return text


def image_to_string(im=None, out='stdout', **kwargs):
    # 因为输出字符串，所以将psm设置为7，表示单行文本
    return image_to_text(im=im, out=out, psm='7', **kwargs)
