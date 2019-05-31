# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.abspath(os.path.abspath(os.path.join(os.path.dirname(__file__),".."))))
from conf.configInfo import *
class UtilTools():

    def __init__(self):
        self.api = 'FTNN'

    def getHistoryday(self,today,days):
        """
        获取当前日期的前几天
        :param today: datetime.date.today(),当前日期
        :param days: 当前日期的前几天
        :return:
        """
        import datetime
        day = datetime.timedelta(days)
        historyday = today - day
        return historyday

    def md5(self,str):
        """返回加密的md5码"""
        import hashlib
        m = hashlib.md5()
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    def sendEmail(self,sender, receivers, content,type=''):
        """
        邮件发送类
        :param sender:
        :param receivers:
        :param content:
        :param type: 类型可选，明文/SSL/TLS
        :return:
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header
        from email.utils import formataddr
        config = ConfigInfo()
        mail_host = config.smtp  # 设置服务器
        mail_port = config.smtp_port  # 各类邮箱产品不同
        user_name = config.email_user
        login_password = config.login_password  # 邮件服务器口令
        list = []
        list.append(receivers)

        # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
        message = MIMEText(content, 'html', 'utf-8')
#         message['From'] = Header(sender, 'utf-8')
#         message['To'] = Header(receivers, 'utf-8')
#         message['From']=formataddr(["发件人昵称",sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
#         message['To']=formataddr(["收件人昵称",receivers])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        message['From']=formataddr(["发件人昵称",user_name])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        message['To']=formataddr(["收件人昵称",receivers])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
 
        subject = sender
        message['Subject'] = Header(subject, 'utf-8')

        try:
            # 连接smtp服务器，明文/SSL/TLS三种方式，根据你使用的SMTP支持情况选择一种
            # 普通方式，通信过程不加密

            if type == 'SSL':
                # 纯粹的ssl加密方式，通信过程加密，邮件数据安全
                smtp = smtplib.SMTP_SSL(mail_host,mail_port)
            elif type == 'TLS':
                # tls加密方式，通信过程加密，邮件数据安全，使用正常的smtp端口
                smtp = smtplib.SMTP(mail_host,mail_port)
                smtp.set_debuglevel(True)
                smtp.ehlo()
                smtp.starttls()
            else:
                smtp = smtplib.SMTP(mail_host, mail_port)

            smtp.ehlo()
            smtp.login(user_name, login_password)
            # 发送邮件
            smtp.sendmail(user_name, list, message.as_string())
            smtp.close()
            return '成功!'
        except Exception as e:
            return '失败,%s!'%e

    def writeLog(self,logInfo):

        import logging

        logging.basicConfig(level=logging.INFO,
                            filename='%s/../log/log.txt' % os.path.dirname(__file__),
                            filemode='a',
                            format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
        logging.info(logInfo)

    def strTotime(self,str):
        """
        时间字符串转换为时间戳
        :param str: YYYY-mm-dd HH:MM:ss
        :return:
        """
        import time
        # 转换成时间数组
        timeArray = time.strptime(str, "%Y-%m-%d %H:%M:%S")
        # 转换成时间戳
        timestamp = time.mktime(timeArray)
        return int(timestamp)

    def drop_duplicates(self,ftnnOrderDataFrame):
        """
        特定方法，谨慎使用
        :param ftnnOrderDataFrame:
        :return:
        """
        tempdata = ftnnOrderDataFrame
        for i in ftnnOrderDataFrame.index:
            flag = False
            for j in tempdata.index:
                if i!=j and ftnnOrderDataFrame.loc[i,'code'] == tempdata.loc[j,'code'] and ftnnOrderDataFrame.loc[j,'order_side'] == tempdata.loc[j,'order_side']:
                    vol = abs(ftnnOrderDataFrame.loc[i,'price']-tempdata.loc[j,'price'])/ftnnOrderDataFrame.loc[i,'price']
                    # print(vol*100)
                    if vol*100<1:
                       flag = True
            if flag:
                tempdata=tempdata.drop(i)
        return tempdata

