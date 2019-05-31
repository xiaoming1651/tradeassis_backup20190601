import sys
import datetime
import argparse

import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from ibapi.wrapper import EWrapper
from ibapi.common import *
from ibapi.ticktype import TickType, TickTypeEnum
from ibapi.client import EClient
from ibapi.utils import *
from ibapi.execution import *
from ibapi.order_condition import *
from ibapi.contract import *
from ibapi.order import *
from ibapi.order_state import *
import queue
import redis;
from util.UtilTools import *;
import time;
import copy;
from futu import *
class TradeAssis(EClient, EWrapper):
    def __init__(self,config:ConfigInfo,host:str,port:int):
        EClient.__init__(self, self)
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.permIdOcaGroup = {}
        self.ibOrdersDict = {}
        self.ibOrders = []
        self.ibCashBalanceDist = {}
        self.accountsSet = set()
        self.execOrder = {}
        self.CNH_HKD_BID = 0
        self.CNH_HKD_ASK = 0
        self.USD_HKD_BID = 0
        self.USD_HKD_ASK = 0
        self.config = config
        self.redis_conn = redis.Redis(config.r_host,config.r_port,config.r_db, config.r_password,decode_responses=True);
        self.a_host = host
        self.a_port = port
    @iswrapper
    def nextValidId(self, orderId:int):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        # print("NextValidId:", orderId)

    def placeOneOrder(self):
        con = Contract()
        con.symbol = "AMD"
        con.secType = "STK"
        con.currency = "USD"
        con.exchange = "SMART"
        order = Order()
        order.action = "BUY"
        order.orderType = "LMT"
        order.tif = "GTC"
        order.totalQuantity = 3
        order.lmtPrice = 1.23
        self.placeOrder(self.nextOrderId(), con, order)

    def cancelOneOrder(self):
        pass

    def nextOrderId(self):
        id = self.nextValidOrderId
        self.nextValidOrderId += 1
        return id

    @iswrapper
    def error(self, *args):
        super().error(*args)
        # print(current_fn_name(), vars())

    @iswrapper
    def winError(self, *args):
        super().error(*args)
        # print(current_fn_name(), vars())

    @iswrapper
    def openOrder(self, orderId:OrderId, contract:Contract, order:Order,
                  orderState:OrderState):
        super().openOrder(orderId, contract, order, orderState)
        # print(current_fn_name(),vars())
        # print("OpenOrder. PermId: ", order.permId,"parentId",order.parentId,"parentPermId",order.parentPermId,"ocaGroup:",order.ocaGroup, "ClientId:", order.clientId,"orderId:",order.orderId,
        #       "Account:", order.account, "Symbol:", contract.symbol, "SecType:", contract.secType,
        #       "Exchange:", contract.exchange, "Action:", order.action, "OrderType:", order.orderType,
        #       "TotalQty:", order.totalQuantity, "CashQty:", order.cashQty,
        #       "LmtPrice:", order.lmtPrice, "AuxPrice:", order.auxPrice, "Status:", orderState.status,"activeStartTime:",order.activeStartTime,
        #       "goodTillDate:",order.goodTillDate,"autoCancelDate:",order.autoCancelDate,"goodAfterTime:",order.goodAfterTime,"completedTime:",orderState.completedTime,
        #       "continuousUpdate:",order.continuousUpdate,"trailStopPrice:",order.trailStopPrice,"startingPrice:",order.startingPrice,
        #       "stockRefPrice:",order.stockRefPrice,"triggerPrice:",order.triggerPrice,"adjustedStopPrice:",order.adjustedStopPrice,
        #       "adjustedStopLimitPrice:",order.adjustedStopLimitPrice)
        # if(order.trailStopPrice == 1.7976931348623157e+308):
        #     print("最大值")
        # if(order.trailStopPrice != 1.7976931348623157e+308):
        #     print("正常值")
        order.contract = contract
        self.permId2ord[order.permId] = order
        self.permIdOcaGroup[order.permId] = order.ocaGroup
        #         self.ibOrders.append({"symbol":contract.symbol,"currency":contract.currency,"action":order.action,"totalQuantity":order.totalQuantity,"lmtPrice":order.lmtPrice})
        self.ibOrdersDict[order.permId] = {"permId":order.permId,"orderId":order.orderId,"parentId":order.parentId,"parentPermId":order.parentPermId,
                                           "ocaGroup":order.ocaGroup,"ocaGroupPrice":0,"symbol":contract.symbol,
                                           "currency":contract.currency,"action":order.action,"totalQuantity":int(order.totalQuantity),
                                           "lmtPrice":order.lmtPrice,'trailStopPrice':order.trailStopPrice,'auxPrice':order.auxPrice,'childNum':0,'orderId':orderId,'secType':contract.secType,
                                           'exchange':contract.exchange,'orderType':order.orderType,'tif':order.tif
                                           }

    @iswrapper
    def accountSummary(self, reqId:int, account:str, tag:str, value:str,
                       currency:str):
        """Returns the data from the TWS Account Window Summary tab in
        response to reqAccountSummary()."""
        super().accountSummary(reqId, account, tag, value, currency)
        #         print("Acct Summary. ReqId:", reqId, "Acct:", account,"Tag: ", tag, "Value:", value, "Currency:", currency)
        if(tag == "CashBalance"):
            print("Acct Summary. ReqId:", reqId, "Acct:", account,"Tag: ", tag, "Value:", value, "Currency:", currency)
            self.ibCashBalanceDist[currency] = float(value)

    @iswrapper
    def accountSummaryEnd(self, reqId: int):
        super().accountSummaryEnd(reqId)
        print("AccountSummaryEnd. Req Id: ", reqId)

    @iswrapper
    def managedAccounts(self, accountsList: str):
        super().managedAccounts(accountsList)
        # print("Account list: ", accountsList)
        self.accountsSet.add(accountsList)

    @iswrapper
    def openOrderEnd(self, *args):
        super().openOrderEnd()

    @iswrapper
    def orderStatus(self,orderId:OrderId , status:str, filled:float,
                    remaining:float, avgFillPrice:float, permId:int,
                    parentId:int, lastFillPrice:float, clientId:int,
                    whyHeld:str,mktCapPrice:str):
        super().orderStatus(orderId, status, filled, remaining,
                            avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld,mktCapPrice)

    @iswrapper
    def tickPrice(self, tickerId: TickerId , tickType: TickType, price: float, attrib):
        super().tickPrice(tickerId, tickType, price, attrib)
        #         print(current_fn_name(), vars())
        #         bid是指卖出外汇的价格，即我要卖出外汇，标一个价格为bid。
        #         ask是指买入外汇的价格，即我要买入外汇，询问得价格为ask。
        if(tickerId == 9005 and TickTypeEnum.to_str(tickType) == "BID" and self.USD_HKD_BID != 0):
            self.USD_HKD_BID = price
        elif(tickerId == 9005 and TickTypeEnum.to_str(tickType) == "ASK" and self.USD_HKD_ASK != 0):
            self.USD_HKD_ASK = price
        #             print(current_fn_name(), tickerId, TickTypeEnum.to_str(tickType), price, attrib, file=sys.stderr)
        elif(tickerId == 9006 and TickTypeEnum.to_str(tickType) == "BID" and self.CNH_HKD_BID != 0):
            self.CNH_HKD_BID = price
        elif(tickerId == 9006 and TickTypeEnum.to_str(tickType) == "ASK" and self.CNH_HKD_ASK != 0):
            self.CNH_HKD_ASK = price
        print(current_fn_name(), tickerId, TickTypeEnum.to_str(tickType), price, attrib, file=sys.stderr)


    @iswrapper
    def tickSize(self, tickerId: TickerId, tickType: TickType, size: int):
        super().tickSize(tickerId, tickType, size)

    @iswrapper
    def scannerParameters(self, xml:str):
        open('scanner.xml', 'w').write(xml)

    def contractDetails(self, reqId:int, contractDetails:ContractDetails):
        super().contractDetails(reqId, contractDetails)
        # print(current_fn_name(), vars())

    def execDetails(self, reqId:int, contract:Contract, execution:Execution):
        super().execDetails(reqId, contract, execution)
        # print(current_fn_name(),vars())
        self.execOrder[execution.permId] = execution.avgPrice

    #通过富途牛牛检查价格是否超过10%
    def checkPriceByFuTu(self,ibOrder):
        symbol = ibOrder['symbol']
        currency = ibOrder['currency']
        action = ibOrder['action']
        modify_price = ibOrder['modify_price']
        if(currency == "USD"):
            if not (symbol == 'XAUUSD' or symbol == 'XAGUSD'):
                symbol = symbol.replace(" ",".")
                symbol = 'US.'+symbol
            else:
                return False
        elif(currency == "HKD"):
            if not (symbol=='CNH' or symbol == 'USD'):
                symbol = "HK."+symbol.zfill(5)
            else:
                return False
        elif(currency == "CNH"):
            if(symbol == '87001'):
                symbol = "HK."+symbol.zfill(5)
            else:
                if(symbol[0] == '6'):
                    symbol = "SH."+symbol
                else:
                    symbol = "SZ."+symbol.zfill(6)
        quote_ctx = OpenQuoteContext(self.config.futuHost, self.config.futuPort)
        code_list = [symbol]
        quote_ctx.subscribe(code_list, [SubType.QUOTE])
        code_list_price = quote_ctx.get_stock_quote(code_list)
        quote_ctx.close()
        last_price = float(code_list_price[1]['last_price'][0])
        print("富途牛牛 ",symbol," 最新价格 ",last_price," 修改价 ",modify_price)
        if(action == 'BUY'):
            if(modify_price < last_price*(1-self.config.maxPercent) or modify_price > last_price):
                return True
        else:
            if(modify_price > last_price*(1+self.config.maxPercent) or modify_price < last_price):
                return True
        return False


    def getIbOrders(self):
        self.reqManagedAccts();
        self.reqOpenOrders();
        # 要修改或取消从TWS手动下达的单个订单，需要连接到客户机ID 0，然后在尝试修改之前绑定订单。绑定过程为订单分配一个API订单ID；在绑定之前，它将以0的API订单ID返回给API。无法从API修改/取消具有API订单ID 0的订单。函数reqopenorders绑定当前打开的订单，这些订单还没有API订单ID，而函数reqautoopenorders自动绑定未来的订单。reqallopenorders函数不绑定订单。
        # app.reqAllOpenOrders() #函数不绑定订单。
        # app.reqOpenOrders();
        # app.reqAutoOpenOrders(True);#自动绑定未来的订单
        execFilter = ExecutionFilter()
        self.reqExecutions(9004, execFilter)
        count = 1
        for index in range(1000):
            try:
                text = self.msg_queue.get(block=True, timeout=0.2)
            except queue.Empty:
                # print("queue.get: empty")
                if(count > 10):
                    break
                count = count + 1
            else:
                # print(str(text))
                invalidTexts = ['afarm','cashfarm','cashhmds','hkhmds','ushmds','secdefhk','jfarm','usfuture','hfarm','usfarm']
                invalidB = False
                for invalidText in invalidTexts:
                    if(invalidText in str(text)):
                        invalidB = True
                        continue
                if(not invalidB):
                    # print("text=%s",text)
                    fields = comm.read_fields(text)
                    # print("fields %s", fields)
                    self.decoder.interpret(fields)
        # app.disconnect()
        # app.run()
        # app.disconnect()
        import copy
        ordersDictC = copy.deepcopy(self.ibOrdersDict)
        for permId,ocaGroup in self.permIdOcaGroup.items():
            for permId2,ocaGroup2 in self.permIdOcaGroup.items():
                if(ocaGroup2 != "" and int(ocaGroup2) == permId):
                    self.ibOrdersDict.pop(permId2)
                    break
        addOrder = []
        for order in self.ibOrdersDict.values():
            if order['ocaGroup'] != "":
                if  self.execOrder.__contains__(int(order['ocaGroup'])):
                    order['ocaGroupPrice'] = self.execOrder[int(order['ocaGroup'])]
                    childNum = order['childNum'];
                    for permId,ocaGroup in self.permIdOcaGroup.items():
                        if(ocaGroup != '' and order['permId'] == int(ocaGroup)):
                            childNum += 1;
                            for permId2,ocaGroup2 in self.permIdOcaGroup.items():
                                if(ocaGroup2 != '' and permId == int(ocaGroup2)):
                                    childNum += 1;
                                    for permId3,ocaGroup3 in self.permIdOcaGroup.items():
                                        if(ocaGroup3 != '' and permId2 == int(ocaGroup3)):
                                            childNum += 1;
                                            if(self.config.maxChildNum == 3):
                                                order['addOrder'] = ordersDictC[permId3]
                                            for permId4,ocaGroup4 in self.permIdOcaGroup.items():
                                                if(ocaGroup4 != '' and permId3 == int(ocaGroup4)):
                                                    childNum += 1;
                                                    if(self.config.maxChildNum == 4):
                                                        order['addOrder'] = ordersDictC[permId3]
                                                    for permId5,ocaGroup5 in self.permIdOcaGroup.items():
                                                        if(ocaGroup5 != '' and permId4 == int(ocaGroup5)):
                                                            childNum += 1;
                                                            break
                                                    break
                                            break
                                    break
                            break

                    order['childNum'] = childNum;
        print("未成交母单：")
        modifyOrders = [];
        for order in self.ibOrdersDict.values():
            print(order)
            #修改母单价格
            if(order['childNum'] >= self.config.maxChildNum and order['ocaGroupPrice']>0 and not self.redis_conn.hget('modify_trade_order',order['permId']) ):
                if(order['action'] == "BUY"):
                    order['modify_price'] = round(order['ocaGroupPrice']*(1-self.config.percent),2)
                else:
                    order['modify_price'] = round(order['ocaGroupPrice']*(1+self.config.percent),2)

                if(order['secType'] == 'STK' and order['currency'] == 'HKD'):
                    order['modify_price'] = (order['modify_price']//0.2)*0.2
                curPrice = order['lmtPrice']
                priceType = 1
                if (curPrice==0 and order['trailStopPrice'] != 1.7976931348623157e+308):
                    curPrice = order['trailStopPrice']
                    priceType = 2
                if(order['modify_price']*(1+self.config.maxPercent) < curPrice or order['modify_price']*(1-self.config.maxPercent) > curPrice):
                    break
                if self.checkPriceByFuTu(order):
                    break
                con = Contract()
                con.symbol = order['symbol']
                con.secType = order['secType']
                con.currency = order['currency']
                con.exchange = order['exchange']
                order_new = Order()
                order_new.action = order['action']
                order_new.orderType = order['orderType']
                order_new.tif = order['tif']
                order_new.totalQuantity = order['totalQuantity']
                if(priceType == 1):
                    order_new.lmtPrice = order['modify_price']
                elif priceType==2:
                    order_new.trailStopPrice = order['modify_price']
                order_new.auxPrice = order['auxPrice']
                self.placeOrder(order['orderId'], con, order_new)
                self.redis_conn.hset('modify_trade_order',order['permId'],str(order))
                modifyOrders.append(order)
                #添加子单
                if(order['childNum'] == self.config.maxChildNum):
                    addOrder = order['addOrder']
                    # print(addOrder)
                    con = Contract()
                    con.symbol = addOrder['symbol']
                    con.secType = addOrder['secType']
                    con.currency = addOrder['currency']
                    con.exchange = addOrder['exchange']
                    order_new = Order()

                    curPrice = addOrder['lmtPrice']
                    priceType = 1
                    if (curPrice==0 and addOrder['trailStopPrice'] != 1.7976931348623157e+308):
                        curPrice = order['trailStopPrice']
                        priceType = 2
                    if(addOrder['action'] == 'BUY'):
                        order_new.action = 'SELL'
                        curPrice = round(curPrice*(1+self.config.percent),2)
                    else:
                        order_new.action = 'BUY'
                        curPrice = round(curPrice*(1-self.config.percent),2)
                    if(addOrder['secType'] == 'STK' and addOrder['currency'] == 'HKD'):
                        curPrice = (curPrice//0.2)*0.2
                    order_new.orderType = addOrder['orderType']
                    order_new.tif = addOrder['tif']
                    order_new.totalQuantity = addOrder['totalQuantity']
                    order_new.ocaGroup = addOrder['permId']
                    order_new.parentId = addOrder['orderId']
                    if(priceType == 1):
                        order_new.lmtPrice = curPrice
                    elif priceType==2:
                        order_new.trailStopPrice = curPrice
                    order_new.auxPrice = addOrder['auxPrice']
                    # print(order_new)
                    self.placeOrder(self.nextValidOrderId, con, order_new)
                    add_order_dict = {'symbol':con.symbol,'secType':con.secType,'currency':con.currency,'exchange':con.exchange,
                                      'action':order_new.action,'orderType':order_new.orderType,'tif':order_new.tif,
                                      'totalQuantity':order_new.totalQuantity,'ocaGroup':order_new.ocaGroup,'parentId':order_new.parentId,
                                      'lmtPrice':order_new.lmtPrice,'trailStopPrice':order_new.trailStopPrice,'auxPrice':order_new.auxPrice,}
                    app.redis_conn.hset('add_trade_child_order',order_new.ocaGroup,str(add_order_dict))
                    modifyOrders.append({'symbol':con.symbol,'action':order_new.action,'totalQuantity':order_new.totalQuantity,'modify_price':curPrice,'operation':'add'})

        # app.disconnect()
        return modifyOrders;

if __name__ == "__main__":
    print("IB Trade assistan V1.0")
    config = ConfigInfo()
    util = UtilTools()
    print("connecting to host: ",config.IBHost," port:",config.IBPort)
    app = TradeAssis(config,config.IBHost, config.IBPort)
    app.connect(app.a_host, app.a_port, 0)
    print("connecting to  host: ",config.IBHost,"port:",config.IBPort2)
    app2 = TradeAssis(config,config.IBHost, config.IBPort2)
    app2.connect(app2.a_host, app2.a_port, 0)
    print("connecting to  host: ",config.IBHost,"port:",config.IBPort3)
    app3 = TradeAssis(config,config.IBHost, config.IBPort3)
    app3.connect(app3.a_host, app3.a_port, 0)
    appList = [app,app2,app3]

    while True:
        modifyOrders = {}
        for app in appList:
            if app.conn and app.conn.isConnected():
                # modifyOrders.extend(getIbOrders(app))
                orders = app.getIbOrders()
                if orders:
                    modifyOrders[",".join(app.accountsSet)] = orders
            else:
                print("can't connect to ",app.a_host," port:",app.a_port)
        trade_records = ""
        firstOrderStr = ""
        for account,orders in modifyOrders.items():
            if(orders):
                print("需修改报价的母单：")
                print(orders)
                trade_records = account+":<br>"
                firstOrderStr = orders[0]['symbol']+" "+orders[0]['action']+" %s@%s" % ( orders[0]['totalQuantity'],orders[0]['modify_price'])
                for order in orders:
                    if('operation' in order and order['operation'] == 'add'):
                        trade_records += "+ "
                    trade_records += order['symbol']+" "+order['action']+" %s@%s" % ( order['totalQuantity'],order['modify_price'])+"<br>"
        if trade_records:
            res ='向%s发送邮件%s' % (str(config.receivers), str(util.sendEmail(time.strftime("%H:%M")+" "+firstOrderStr, config.receivers, trade_records, 'SSL')))
            print(res)
        else:
            print("无符合条件的母单")
        time.sleep(300)
    #     # break