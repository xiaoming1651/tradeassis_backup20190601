# -*- coding: utf-8 -*-
#富途牛牛常量文件
# 订单类型
ORDERTYPR = {
    0: '普通交易',
    1: '竞价单',
    3: '竞价限价单'
}
# 交易方向
ORDERSIDE = {
    0: '买',
    1: '卖'
}
# 返回的订单状态
ORDERSTATUS = {
    0:'服务器处理中',
    1:'等待成交',
    3:'全部成交',
    4:'已失效',
    5:'下单失败',
    6:'已撤单',
    7:'已删除',
    8:'等待开盘',
    21:'本地已发送',
    22:'本地已发送，服务器返回下单失败、没产生订单',
    23:'本地已发送，等待服务器返回超时'
}

#数据库字段列表
"""
  id 数据库订单号
  fid
  tradef
  function
  platform
  symbol
  exchange
  action
  currency
  quantity
  exQuantity
  price
  exPrice
  minProfit
  lossLimit
  fBrokerOrderId
  orderTime
  exTime
  validDate
  fUserName
  USAmount
  HKAmount
  isAuto
  adjustPrice
  status
"""
TRADEORDER = ['fid', 'tradef', 'function', 'platform', 'symbol', 'exchange',
       'action', 'currency', 'quantity', 'exQuantity', 'price', 'exPrice',
       'minProfit', 'lossLimit', 'fBrokerOrderId', 'orderTime', 'exTime',
       'validDate', 'fUserName', 'USAmount', 'HKAmount', 'isAuto',
       'adjustPrice', 'status']