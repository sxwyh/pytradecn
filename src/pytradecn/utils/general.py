#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：工具库
# 建立日期：2022.11.17
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
#   2022-11-17  第一次编写
#   2024-02-12  添加识别软件安装路径方法
#

import winreg

from subprocess import run, PIPE, STDOUT
from time import sleep
from os.path import dirname


def command(cmd: str) -> str:
    # 发送并执行cmd指令
    return run(cmd, stdout=PIPE, stderr=STDOUT, shell=True, timeout=None,
               encoding='gbk').stdout.replace('\r', '').replace('\n\n', '\n').strip()


# def logger(*args, sep=' ', end='\n'):
#    # 打印日志
#    path = os.getcwd() + r'\log'
#    if not os.path.exists(path): os.mkdir(path)
#    file = path + '\\' + strftime("%Y-%m-%d", localtime()) + '.log'
#    log = '[' + strftime("%H:%M:%S", localtime()) + '] ' + sep.join(args) + end
#    with open(file, 'a') as f: f.write(log)
#    print('[' + strftime("%H:%M:%S", localtime()) + ']', *args, sep=sep, end=end)


def wait(s):
    sleep(s)


def get_app_path(app):
    keys = [
        (winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall')
    ]

    for key in keys:
        # reg_hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_READ)
        reg_hkey = winreg.OpenKey(*key)
        for i in range(0, winreg.QueryInfoKey(reg_hkey)[0]):
            app_hkey = winreg.OpenKey(reg_hkey, winreg.EnumKey(reg_hkey, i))
            # noinspection PyBroadException
            try:
                name = winreg.QueryValueEx(app_hkey, 'DisplayName')[0]
            except Exception:
                continue

            if app.lower() in name.lower():
                # noinspection PyBroadException
                try:
                    return winreg.QueryValueEx(app_hkey, 'InstallLocation')[0]
                except Exception:
                    pass

                # noinspection PyBroadException
                try:
                    uninstall = winreg.QueryValueEx(app_hkey, 'UninstallString')[0]
                    return dirname(uninstall[uninstall.rindex(':') - 1:])
                except Exception:
                    pass

    return None
