import websocket, json, pprint, talib, numpy
import config
import sys, time, os, math
from binance.client import Client
from binance.enums import *
from utils import *

#TRADE_SYMBOL    = "THETAUSDT"
TRADE_SYMBOL    = "BTCUSDT"
TRADE_QUANTITY  = 10


#client = Client(config.API_KEY, config.API_SECRET )

class Broker:
    def __init__(self):
        self.live            = False
        self.begincash       = 300.0
        self.cash            = self.begincash
        self.cryptoamount    = 0.0
        self.avgprice        = 0.0
        self.fee             = 0.001
        self.profit          = 0.0

        self.print_obos      = False

        self.cur_close       = 0.0
        self.ntrades         = 0
        self.date_time       = 0

    def goLive(self):
        print("Broker set to live!")
        self.live = True

    def isLive(self):
        return self.live

    def setDateTime(self, date_time ):
        self.date_time = date_time

    def order(self, side, quantity, symbol, price, order_type=ORDER_TYPE_MARKET):
        try:
            if self.live:

                print("LIVE: sending order:",timestamp2str(self.date_time), symbol,side,quantity,price,order_type)
                #order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)

            else:

                print("REPLAY: sending order:",timestamp2str(self.date_time), symbol,side,quantity,price,order_type)

            #print(order)
        except Exception as e:
            print("an exception occured - {}".format(e))
            return False

        return True
  
    def getOrderAmount(self, amount):
    # DGB - ordered 16000, obtained 15984
    # 15984.0/16000 = 0.999

        minimum   = 0.001  
        increment = 0.0001

        if amount < minimum: return 0.0

        n_increments = math.floor( (amount / increment) * (1 - self.fee) )
        amount       = round(n_increments * increment, 4)

        if amount < minimum: return 0.0

        return amount



    def buyBuyBuy(self, fraction, price):

        #print( "buy", fraction, price)

        avcash = self.cash * (1-self.fee)

        n2buy = self.getOrderAmount( (avcash/price) * fraction )

        if n2buy <= 0: return

        # put binance buy order logic here
        order_succeeded = self.order(SIDE_BUY, n2buy, TRADE_SYMBOL, price)

        if order_succeeded:
            tot_price = self.cryptoamount * self.avgprice
            buy_price = n2buy*price*(1+self.fee) 

            self.cryptoamount = self.cryptoamount + n2buy
            self.cash = self.cash - buy_price
            print( "crypto: ", self.cryptoamount, "cash: ", self.cash)

            tot_price = tot_price + buy_price

            self.avgprice = tot_price/self.cryptoamount


    def sellSellSell(self, fraction, price):
        #print( "sell", fraction, price)

        avcoins = self.cryptoamount * (1-self.fee)

        n2sell = self.getOrderAmount( avcoins * fraction )

        if n2sell <= 0: return

        # put binance sell logic here
        order_succeeded = self.order(SIDE_SELL, n2sell, TRADE_SYMBOL, price)

        if order_succeeded:
            tot_price = self.cryptoamount * self.avgprice
            sell_price = n2sell*price*(1-self.fee) 

            self.cryptoamount = self.cryptoamount - n2sell
            self.cash = self.cash + sell_price
            print( "crypto: ", self.cryptoamount, "cash: ", self.cash)

            tot_price = tot_price - sell_price

            self.avgprice = tot_price/self.cryptoamount


            self.profit = 100*(self.cash-self.begincash)/self.begincash
            self.ntrades = self.ntrades + 1

            print( "Total profit : {0:.3f}% in".format(self.profit), self.ntrades, "trades." )


