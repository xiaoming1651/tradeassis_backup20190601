# -*- coding: utf-8 -*-
import configparser
import os
import sys

import binascii

sys.path.append(os.path.abspath(os.path.abspath(os.path.join(os.path.dirname(__file__),".."))))
class ConfigInfo():
    """
    加载配置文件
    """
    def __init__(self):
        """
        加载配置文件
        """
        config = configparser.ConfigParser()
        path = '%s\%s' % (os.path.dirname(__file__), 'config.conf')
        #print("The path is ",path)
        # path = 'D:\\java\\StockUpdate\\futuquant-master\\conf\\config.conf
        config.read(path)
        # print(path)
        # self.futuIp = config['FTNN']['futuIp']
        # self.futuPort = int(config['FTNN']['futuPort'])
        # self.host = config['info']['host']
        # self.user = config['info']['user']
        # self.pwd = config['info']['pwd']
        # self.dbName = config['info']['dbName']
        # self.tradedbName = config['info']['tradedbName']
        self.smtp = config['email']['smtp']
        self.smtp_port = config['email']['smtp_port']
        self.email_user = config['email']['email_user']
        self.receivers = config['email']['receivers']
        # self.receivers2 = config['email']['receivers2']
        self.login_password = config['email']['login_password']
        self.IBHost = config['IB']['IBHost']
        self.IBPort = int(config['IB']['IBPort'])
        # self.IBName = config['IB']['IBName']
        # self.IBHost2 = config['IB']['IBHost2']
        self.IBPort2 = int(config['IB']['IBPort2'])
        self.IBPort3 = int(config['IB']['IBPort3'])
        # self.IBName2 = config['IB']['IBName2']
        # self.clientId = config['IB']['clientId']
        # self.IBDeviate = config['IB']['deviate']
        # self.exchange_rate_US = config['IB']['exchange_rate_US']
        # self.exchange_rate_CN = config['IB']['exchange_rate_CN']
        self.percent = float(config['IB']['percent'])
        self.maxPercent = float(config['IB']['maxPercent'])
        self.maxChildNum = int(config['IB']['maxChildNum'])
        self.r_host = config['redis']['r_host']
        self.r_port = int(config['redis']['r_port'])
        self.r_password = config['redis']['r_password']
        self.r_db = int(config['redis']['r_db'])
        self.futuHost = config['FTNN']['futuHost']
        self.futuPort = int(config['FTNN']['futuPort'])


    def openTrade(self):
        """
          打开港股交易环境
        """
        self.tradehk_ctx = OpenHKTradeContext(host=self.futuIp, port=self.futuPort)
        return self.tradehk_ctx

    def openOpenQuoteContext(self):
        """
           打开股票行情交易环境
        :return:quote_ctx
        """
        self.quote_ctx = ft.OpenQuoteContext(host=self.futuIp,port=self.futuPort)
        return self.quote_ctx

    def getTradePassWord(self):
        file_name = '%s/../data/password.txt' % os.path.dirname(__file__)
        print(file_name)
        file_object = open(file_name)
        try:
            trade_password_md5 = binascii.a2b_hex(file_object.read()).decode('utf-8')
        finally:
            file_object.close()
        return trade_password_md5