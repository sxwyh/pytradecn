#
# 券商客户端自动化测试库
# Copyright (C) 2023 谁的谁（41715399@qq.com） All rights reserved.
#
# 模块功能：邮件发送
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
#   2023-10-13  第一次编写
#

from os.path import basename

from smtplib import SMTP_SSL, SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from email.utils import formataddr


server = 'smtp.qq.com'
user = '41715399@qq.com'
password = '您的密码'


class Email:

    def __init__(self, subject='未设置主题'):
        self.__subject = subject
        self.__mail = MIMEMultipart('related')

    def content(self, text='这是一封邮件', images=None, atts=None):
        """邮件正文
        text:  邮件正文内容，默认为空字符，其值可以为普通文本或HTML
               text = '这是我的正文'  # 普通的文本
               text = '<p><b>这是我的正文</b></p>'  # HTML文本
        images:图像列表，默认为None，其值可以单个硬盘图像、单个文件对象、或他们组成的元组
               images = 'd:/123.jpg'  # 字符串形式的单文件图像
               images = file对象  # 单图像文件对象 open()已打开的文件对象或PIL文件对象
               images = ('d:/123.jpg', file, 'd:/456.jpg')  # 他们组成的元组
        atts:  附件或附件列表，默认为None，其值可以为单个硬盘文件或他们组成的元组
               atts = 'd:/123.docx'  # 字符串形式的单个文件
               atts = ('d:/123.docx', 'd:/456.docx')  # 附件字符串组成的元组
        """
        if images is not None and not isinstance(images, tuple):
            images = (images,)

        if atts is not None and isinstance(atts, str):
            atts = (atts,)

        # 邮件正文
        if images is not None:
            for i, image in enumerate(images, start=1):
                text = text + rf'<p><img src="cid:image{i}"></p>'
                if isinstance(image, str):
                    with open(image, 'rb') as f:
                        # img = MIMEImage(f.read(), _subtype=False)
                        img = MIMEImage(f.read())
                else:
                    img = image
                img.add_header('Content-ID', f'<image{i}>')
                self.__mail.attach(img)

        if atts is not None:
            for file in atts:
                att = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
                att["Content-Type"] = 'application/octet-stream'
                # att["Content-Disposition"] = 'attachment; filename="' + basename(file) + '"'
                att.add_header('Content-Disposition', 'attachment', filename=('gbk', '', basename(file)))
                self.__mail.attach(att)

        # 必须将text放在最后
        if text != '':
            self.__mail.attach(MIMEText(text, 'html', 'utf-8'))

    def send(self, receivers, sender=user):
        """发送邮件
        receivers: 邮件接收者，必填项，其值可以为单个字符串地址、字符串地址列表、名称和字符串组成的元组、元组列表、或他们的混合列表
               receivers = '12345@qq.com'  # 字符串表示的邮件地址
               receivers = ['12345@qq.com', '67890@qq.com']  # 字符串邮件地址列表
               receivers = ('12345@qq.com', '67890@qq.com')  # 字符串邮件地址列表
        sender: 邮件发送者，默认为 41715399@qq.com，其值可以为名称字符串、或名称和地址组成的二元组
               sender = '张三'  # 字符串，发送者的机构或名称
               sender = ('张三', '12345@qq.com')  # 发送者名称（机构）和地址组成的二元组
        """
        if isinstance(receivers, str):
            receivers = [receivers, ]

        if isinstance(sender, str):
            sender = (sender, user)

        # 邮件头
        # self.__mail['From'] = formataddr((Header(sender[0], 'utf-8').encode(), sender[1]))
        self.__mail['From'] = formataddr(sender)
        self.__mail['To'] = ';'.join(receivers)
        self.__mail['Subject'] = Header(self.__subject, 'utf-8')

        # 发送邮件
        try:
            smtp = SMTP_SSL(server)
            # 我们用set_debuglevel(1)就可以打印出和SMTP服务器交互的所有信息。
            # smtp.set_debuglevel(1)
            smtp.login(user, password)
            smtp.sendmail(sender[1], receivers, self.__mail.as_string())
            smtp.quit()
        except SMTPException:
            pass
