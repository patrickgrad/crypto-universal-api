import hmac
import hashlib
import time
import urllib
import urllib2
import json
import cua_statuses as s
import cua_market as m

class cex_api:
    # Init class
    def __init__(self, username, api_key, secret):
        self.NAME = "CEX.io"
        self.INDEX = ''
        self.USERNAME = username
        self.APIKEY = api_key
        self.SECRET = secret
        self.NONCE = ''
        self.RATE = 1 #1 call per second allowed
        self.BALANCES = ''
        self.MARKETS = []

    # get timestamp as nonce
    def __nonce(self):
        self.NONCE = '{:.10f}'.format(time.time() * 1000).split('.')[0]

    # generate segnature
    def __signature(self):
        string = self.NONCE + self.USERNAME + self.APIKEY  # create string
        signature = hmac.new(self.SECRET, string, digestmod=hashlib.sha256).hexdigest().upper()  # create signature
        return signature

    def __post(self, url, param):  # Post Request (Low Level API call)
        params = urllib.urlencode(param)
        req = urllib2.Request(url, params, {'User-agent': 'bot-cex.io-' + self.USERNAME})
        page = urllib2.urlopen(req).read()
        return page

    def api_query(self, method, param={}, private=0, couple=''):  # api call (Middle level)
        url = 'https://cex.io/api/' + method + '/'  # generate url
        if couple != '':
            url = url + couple + '/'  # set couple if needed
        if private == 1:  # add auth-data if needed
            self.__nonce()
            param.update({
                'key': self.APIKEY,
                'signature': self.__signature(),
                'nonce': self.NONCE})
        answer = self.__post(url, param)  # Post Request
        return json.loads(answer)  # generate dict and return

    def ticker(self, couple='GHS/BTC'):
        return self.api_query('ticker', {}, 0, couple)

    def refreshOrderBook(self, pair):
        if pair == '':
            for mar in self.MARKETS:
                mar.refreshOrderBook()

        else:
            p = pair[1] + "/" + pair[0]
            book = self.api_query('order_book', {}, 0, p)
            del book['buy_total']
            del book['sell_total']
            del book['pair']
            del book['id']
            return book

    def refreshTradeHistory(self, pair, since=1):
        if pair == '':
            for mar in self.MARKETS:
                mar.refreshTradeHistory()

        else:
            p = pair[1] + "/" + pair[0]

            hist = self.api_query('trade_history', {"since": str(since)}, 0, p)
            return hist

    def refreshBalances(self):
        bal = self.api_query('balance', {}, 1)
        if(bal.has_key('error')):
            print(s.red(self.NAME) + bal['error'])
            return False
        else:
            bal.pop('username')
            bal.pop('timestamp')
            for cur in bal.iterkeys():
                bal[cur]['onOrder'] = bal[cur].pop('orders')

            self.BALANCES = bal
            return True


    def refreshOpenOrders(self, pair):
        if pair == '':
            for m in self.MARKETS:
                m.refreshOpenOrders()

        else:
            p = pair[1] + "/" + pair[0]
            return self.api_query('open_orders', {}, 1, p)

    def cancel_order(self, order_id):
        return self.api_query('cancel_order', {"id": order_id}, 1)

    def place_order(self, ptype='buy', amount=1, price=1, couple='GHS/BTC'):
        return self.api_query('place_order', {"type": ptype, "amount": str(amount), "price": str(price)}, 1, couple)

    def price_stats(self, last_hours, max_resp_arr_size, couple='GHS/BTC'):
        return self.api_query(
                'price_stats',
                {"lastHours": last_hours, "maxRespArrSize": max_resp_arr_size},
                0, couple)

    def getMarket(self, pair): #-call on an api to return a market
        mkt = m.market(pair,self)
        self.MARKETS.append(mkt)
        return mkt
