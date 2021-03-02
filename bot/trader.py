import websocket, json, pprint, talib, numpy
import config
import sys, time, os
from binance.client import Client
from binance.enums import *
from utils import *
from Sma  import *
#from Rsi  import *
from Ema  import *
from Macd import *



class Trader:
    def __init__(self, broker,parameters=None):

        len_fac         = 60
        sma_length      = len_fac * 200
        ema_length      = len_fac * 20
        #rsi_length      = len_fac * 20
        fast_length     = len_fac * 23 
        slow_length     = len_fac * 26
        macd_length     = len_fac * 9
        emamacd_length  = len_fac * 9


        #rsi_K           = (2.0 / (1+rsi_length))
        ema_K           = (2.0 / (1+ema_length))
        fast_K          = (2.0 / (1+fast_length))
        slow_K          = (2.0 / (1+slow_length))
        macd_K          = (2.0 / (1+macd_length))
        emamacd_K       = (2.0 / (1+emamacd_length))

        self.sma_fac = 1.0
        self.ema_fac = 1.0
        self.mac_fac = 1.0
        self.offset  = 0.0

        #self.rsi_overbought  = 70
        #self.rsi_oversold    = 30

        if parameters is None:
            dprint("Trader started with default parameters:")
             
            par = {}
            par['sma_length'] = sma_length
            par['ema_K']      = ema_K
            par['fast_K']     = fast_K
            par['slow_K']     = slow_K
            par['macd_K']     = macd_K
            par['emamacd_K']  = emamacd_K
            '''
            par['sma_fac']    = self.sma_fac
            par['ema_fac']    = self.ema_fac
            par['mac_fac']    = self.mac_fac
            par['offset']     = self.offset
            '''

            dpprint(par)

        else:
            dprint("Trader started with  parameters:")
             
            sma_length     = parameters['sma_length']
            ema_K          = parameters['ema_K']
            fast_K         = parameters['fast_K']
            slow_K         = parameters['slow_K']
            macd_K         = parameters['macd_K']
            emamacd_K      = parameters['emamacd_K']
            '''
            self.sma_fac   = parameters['sma_fac']
            self.ema_fac   = parameters['ema_fac']
            self.mac_fac   = parameters['mac_fac']
            self.offset    = parameters['offset']
            '''

            dpprint(parameters)

        dprint("lengths:")

        ppar = {}
        ppar['sma_length']     = sma_length
        #ppar['rsi_length']     = 2.0/rsi_K - 1
        ppar['ema_length']     = 2.0/ema_K - 1
        ppar['fast_length']    = 2.0/fast_K - 1
        ppar['slow_length']    = 2.0/slow_K - 1
        ppar['macd_length']    = 2.0/macd_K - 1
        ppar['emamacd_length'] = 2.0/emamacd_K - 1

        dpprint(ppar)
 

        self.broker = broker
        self.candles = []

        # SMA Indicator - Are we in a Bull or Bear market according to 200 SMA?
        self.sma = Sma(sma_length)

        # RSI Indicator
        #self.rsi = Rsi(rsi_length,rsi_K)

        # EMA Indicator - Are we in a rally or not?
        self.ema = Ema(ema_length,ema_K)

        # MACD Indicator - Is the MACD bullish or bearish?
        # MACD = ema(close, fastLength) - ema(close, slowlength)
        self.macd    = Macd( (fast_length,slow_length,macd_length), (fast_K,slow_K,macd_K) )

        # emaMACD = ema(MACD, MACDLength)
        #self.emamacd = EmaMacd(MACD_LENGTH)
        self.emamacd = Ema(emamacd_length,emamacd_K)

    def append(self, candle):
        # check if valid input
        self.validateInput(candle)
        # check for virtual candle
        if len(self.candles) > 0 and self.candles[-1] == candle:
            self.candles = self.candles[:-1]

        self.candles.append(candle) 
        self.calculate(candle)
        self.broker.setDateTime(candle['T'])
        
    
    # Stragegy : MACD/EMA Long Strategy
    # Source   : https://www.tradingview.com/script/o97VVZNr-MACD-EMA-Long-Strategy/
    def calculate(self, candle):

        if self.broker.live:
            print('.', end='')
            sys.stdout.flush()

        cur_sma = self.sma.appendCandle(candle)
        #print("the current sma is {}".format(cur_sma))

        #cur_rsi = self.rsi.appendCandle(candle)
        #print("the current rsi is {}".format(cur_rsi))

        cur_ema = self.ema.appendCandle(candle)   
        #print("the current ema is {}".format(cur_ema))

        cur_macd = self.macd.appendCandle(candle)
        #print("the current macd is {}".format(cur_macd))

        if cur_macd == None:
            cur_macd = 0.0    # ToDo Fix and perhaps use EmaMacd class

        cur_emamacd = self.emamacd.append(candle['T'], cur_macd)
        #print("the current emaMacd is {}".format(cur_emamacd))

        #print(self.emamacd)

        # delta = MACD - aMACD
        delta = 0.0
        if cur_macd != None and cur_emamacd != None:
            delta = cur_macd - cur_emamacd
        #print("the current delta is {}".format(delta))

        cur_close = candle['c']

        if cur_sma == None:
            return

        if cur_close == None:
            return

        if cur_ema == None:
            return

        if cur_macd == None:
            return

        if cur_emamacd == None:
            return

 
        # something wrong, prints different values as above. 
        #print(timestamp2str(candle['T']) +
        #    " close: {0:.2f}, sma: {0:.2f}, ema: {0:.2f}, macd: {0:.2f}, emamacd: {0:.2f}, delta {0:.2f}"
        #    .format(cur_close).format(cur_sma).format(cur_ema).format(cur_macd).format(cur_emamacd).format(delta))


        # 
        # // Set Buy/Sell conditions
        # 

        if cur_close > cur_sma:
            #buy_entry = delta>0 and cur_rsi>self.rsi_overbought
            buy_entry = delta>0 
        else:
            #buy_entry = delta>0 and cur_close>cur_ema and cur_rsi>self.rsi_overbought
            buy_entry = delta>0 and cur_close>cur_ema

        if buy_entry and not self.broker.in_position:
            self.broker.buyBuyBuy(cur_close - cur_sma, cur_close) # ToDo - pass sensible value)
            #print("Current RSI: ",cur_rsi )

        if cur_close < cur_sma:
            #sell_entry = delta<0 and cur_rsi<self.rsi_oversold
            sell_entry = delta<0
        else:
            #sell_entry = delta<0 and cur_close<cur_ema and cur_rsi<self.rsi_oversold
            sell_entry = delta<0 and cur_close<cur_ema

        if sell_entry and self.broker.in_position:
            self.broker.sellSellSell(cur_sma-cur_close, cur_close) # ToDo - pass sensible value)
            #print("Current RSI: ",cur_rsi )


        '''
        # ToDo : linear combination
        rel2sma = cur_close/cur_sma - 1
        #print("the current rel2sma is {}".format(rel2sma))

        rel2ema = cur_close/cur_ema - 1 
        #print("the current rel2ema is {}".format(rel2ema))

        relmacd = cur_macd/cur_emamacd - 1
        #print("the current relmacd is {}".format(relmacd))


        indicator = self.sma_fac*rel2sma + self.ema_fac*rel2ema + self.mac_fac*relmacd + self.offset
        #print("the current signal is {}".format(signal))

        if indicator > 0.5:
            self.broker.buyBuyBuy(cur_close - cur_sma, cur_close) # ToDo - pass sensible value)

        elif indicator < -0.5:
            self.broker.sellSellSell(cur_sma-cur_close, cur_close) # ToDo - pass sensible value)
        '''


    def validateInput(self, candle):
        if type(candle) is not dict:
            raise Exception('invalid input: should be a dict with (c, T, o, h, l, v); input: %s' % (candle, ))
        if len(candle) < 6:
            raise Exception('invalid input: dict length should be 6 or more; input: %s' % (candle, ))
        if not type(candle['T']) is int:
            raise Exception('invalid input: dict element ["T"] should be an int; input: %s' % (candle[0], ))
        for i in {'c', 'o', 'h', 'l', 'v' }:
            if type(candle[i]) is not int and type(candle[i]) is not float:
                raise Exception('invalid input: dict element [%s] is not int or float; input: %s' % (i, candle[i]))
            elif candle[i] < 0:
                raise Exception('invalid input: dict element [%s] is less than 0; input: %s' % (i, candle[i]))
        if candle['h'] < candle['l']:
            raise Exception('invalid input: high: %s is lower than low: %s' % (candle['h'], candle['l']))
        if candle['o'] > candle['h'] or candle['o'] < candle['l']:
            raise Exception('invalid input: open (%s) is outside high (%s) - low (%s) range' % (candle['o'], candle['h'], candle['l']))
        if candle['c'] > candle['h'] or candle['c'] < candle['l']:
            raise Exception('invalid input: close (%s) is outside high (%s) - low (%s) range' % (candle['c'], candle['h'], candle['l']))

