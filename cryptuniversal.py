#The purpose of this project is to establish a standard API for
#accessing all cryptocurrrency exchanges.

import csv

import cua_market as m
import cua_statuses as s

import poloniex as pol
import cex

import os

def start_api(api):
	if(api.refreshBalances()):
		print(s.SUCCESS + "Connected to " + api.NAME)
		return True
	else:
		print(s.ERROR + "Unable to connect to " + api.NAME)
		return False

def load_apis():
    keys = {}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/keys.csv', 'rb') as csvfile:
        r = csv.reader(csvfile)
        i = 0
        a = []
        for row in r:
            if i == 0:
                a = row
            else:
                keys[row[0]] = {}
                dic = keys[row[0]]
                for col in range(1,len(row)):
                    if col != "":
                        dic[a[col]] = row[col]
            i += 1

    n = 0
    apis = []

    if(keys.has_key("cex")):
	    c = keys["cex"]
	    capi = cex.cex_api(c["username"],c["public key"],c["private key"])
	    if(start_api(capi)):
	    	apis.append(capi)
	    	capi.INDEX = n
	    	n += 1
    
    if(keys.has_key("poloniex")):
	    p = keys["poloniex"]
	    papi = pol.poloniex_api(p["public key"],p["private key"])
	    if(start_api(papi)):
	    	apis.append(papi)
	    	papi.INDEX = n
	    	n += 1
            
    return apis

apis = load_apis()

for a in apis:
	mkt = a.getMarket(("USD","BTC"))
	print(mkt.API.NAME)
	print(mkt.PAIR)
	mkt.refreshTradeHistory()
	print(mkt.HISTORY)
	print("")
