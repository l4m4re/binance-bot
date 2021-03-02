import websocket, json, pprint, talib, numpy
import config
import sys, time, os
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
        self.in_position     = False

        self.print_obos      = False

        self.cur_close       = 0.0
        self.last_buy        = 0.0
        self.avgprofit       = 0.0
        self.mresult         = 0.0
        self.ntrades         = 0
        self.profits         = []
        self.results         = []
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


    def buyBuyBuy(self, amount, price):

        if self.in_position:
            if self.print_obos:
                print(timestamp2str(self.date_time), "It is oversold at", price, " but you already own it, nothing to do.")
        else:
            #print("Oversold! Buy! Buy! Buy!")
            # put binance buy order logic here
            order_succeeded = self.order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL, price)
            if order_succeeded:
                self.last_buy = price
                self.in_position = True


    def sellSellSell(self, amount, price):

        if self.in_position:
            #print("Overbought! Sell! Sell! Sell!")
            # put binance sell logic here
            order_succeeded = self.order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL, price)
            if order_succeeded:
                self.in_position = False
                self.last_sell = price
                profit = 100*(self.last_sell-self.last_buy)/self.last_buy
                print( "Profit              : {0:.3f}%".format(profit) )
                self.profits.append(profit)

                result = self.last_sell/self.last_buy
                print( "Result              : {0:.3f}".format(result) )
                self.results.append(result)

                self.avgprofit = calc_average(self.profits)

                self.mresult = 1.0
                for r in self.results:
                   self.mresult = r * self.mresult * 0.995 # calculate 0.5% fee

                self.ntrades = len(self.profits)

                print( "Average profit       : {0:.2f}% in".format(self.avgprofit), self.ntrades, "trades." )
                print( "Multiplicative result: {0:.2f}x in".format(self.mresult), self.ntrades, "trades." )

        else:
            if self.print_obos:
                print(timestamp2str(date_time), "It is overbought at", cur_close, "  but we don't own any. Nothing to do.")

