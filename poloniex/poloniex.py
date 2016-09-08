import hmac
import hashlib
import time
import urllib
import urllib2
import json
import cua_statuses as s
import cua_market as m

class poloniex_api:
    def __init__(self, APIKey, Secret):
        self.NAME = "Poloniex"
        self.INDEX = ''
        self.APIKEY = APIKey
        self.SECRET = Secret
        self.RATE = 6 #6 calls per second allowed
        self.BALANCES = ''
        self.MARKETS = []

    def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
        return time.mktime(time.strptime(datestr, format))

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                            
        return after

    def api_query(self, command, req={}):

        if(command == "returnTicker" or command == "return24Volume"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif(command == "returnOrderBook"):
            ret = urllib2.urlopen(urllib2.Request('http://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif(command == "returnTradeHistory"):
            ret = urllib2.urlopen(urllib2.Request('http://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.urlencode(req)

            sign = hmac.new(self.SECRET, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKEY
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers))
            jsonRet = json.loads(ret.read())
            return self.post_process(jsonRet)


    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def refreshOrderBook(self, pair):
        if pair == '':
            for mar in self.MARKETS:
                mar.refreshOrderBook()

        else:
            if pair[0] == "USD":
                p = "USDT"
            else:
                p = pair[0]

            p += "_" + pair[1]

            book = self.api_query("returnOrderBook", {'currencyPair': p})
            del book['seq']
            return book

    # Returns all of your balances.
    # Outputs: 
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def refreshBalances(self):
        bal = self.api_query('returnCompleteBalances')
        if(bal.has_key('error')):
            print(s.red(self.NAME) + bal['error'])
            return False
        else:
            for cur in bal.iterkeys():
                bal[cur]['onOrder'] = bal[cur].pop('onOrders')
                del bal[cur]['btcValue']

            self.BALANCES = bal
            return True

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def refreshOpenOrders(self,pair):
        if pair == '':
            for mar in self.MARKETS:
                mar.refreshOpenOrders()

        else:
            if pair[0] == "USD":
                p = "USDT"
            else:
                p = pair[0]

            p += "_" + pair[1]
            return self.api_query('returnOpenOrders',{"currencyPair":p})


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs: 
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def refreshTradeHistory(self,pair):
        if pair == '':
            for mar in self.MARKETS:
                mar.refreshTradeHistory()

        else:
            if pair[0] == "USD":
                p = "USDT"
            else:
                p = pair[0]

            p += "_" + pair[1]

            print p

            hist = self.api_query('returnTradeHistory',{"currencyPair":p})
            return hist

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs: 
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs: 
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs: 
    # succes        1 or 0
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."} 
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs: 
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})


    def getMarket(self, pair): #-call on an api to return a market
        mkt = m.market(pair,self)
        self.MARKETS.append(mkt)
        return mkt


