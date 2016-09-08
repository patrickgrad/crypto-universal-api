The standard library of functions that will compose the Universal API are the following:

-cex_api() -returns instance of CEX.io API
-poloniex_api() -returns instance of Poloniex API
kracken_api() -returns instance of Kracken API
gdax_api() -returns instance of GDAX API

-getMarket(self, pair) -call on an api to return a market
-refreshOrderBook(self) -call on a market to refresh the order book variable in the market instance
refreshOpenOrders -call on a market to get the open orders for that market
	^^TODO:standardize the order records for each API
refreshTradeHistory(self) -call on a market to get ALL trade history for that market
	^^TODO:standardize the order records for each API

-refreshBalances(self) -call on an api object to get the currency balances 
-refreshOpenOrders(self) -call on a an api object to get all open orders
-refreshTradeHistory(self) -call on an api object to get all trade history

buyOrder(self, price) -call on a market to place a basic limit order (maker)
buyOrder(self) -call on a market to place a market order (taker)
sellOrder(self, price) -call on a market to place a basic limit order (maker)
sellOrder(self) -call on a market to place a market order (taker)

cancelOrder(self,orderNumber) -call on a market or api to cancel the specified order
withdrawFunds(self,ticker,amount,address) -call on an api to withdraw the specified funds

If a function is not availible then an orderly error should trigger.