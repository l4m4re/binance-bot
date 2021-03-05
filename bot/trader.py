import websocket, json, pprint, talib, numpy
import config
import sys, time, os, math
from binance.client import Client
from binance.enums import *
from utils import *
from Sma  import *
from Rsi  import *
from Ema  import *
from Macd import *



class Trader:
    def __init__(self, broker,parameters=None):

        len_fac         = 60
        sma_len_fac     = 200
        rsi_len_fac     = 20
        ema_len_fac     = 20
        macd_len_fac    = 20
        fast_multiplier = 23.0/20
        slow_multiplier = 26.0/20
        macd_multiplier = 9.0/20

        sma_length      = int(round(len_fac * sma_len_fac))
        rsi_length      = int(round(len_fac * rsi_len_fac))
        ema_length      = int(round(len_fac * ema_len_fac))
        fast_length     = int(round(len_fac * macd_len_fac * fast_multiplier))
        slow_length     = int(round(len_fac * macd_len_fac * slow_multiplier))
        macd_length     = int(round(len_fac * macd_len_fac * macd_multiplier))
        emamacd_length  = macd_length

        rsi_K           = (2.0 / (1+rsi_length))
        ema_K           = (2.0 / (1+ema_length))
        fast_K          = (2.0 / (1+fast_length))
        slow_K          = (2.0 / (1+slow_length))
        macd_K          = (2.0 / (1+macd_length))
        emamacd_K       = (2.0 / (1+emamacd_length))

        self.sma_fac    = 1.0
        self.rsi_fac    = 0.01 
        self.ema_fac    = 1.0
        self.mac_fac    = 1.0
        self.offset     = 0.0

        self.oversold   = -0.13410494
        self.overbought =  0.12345679

        self.cur_close  = 0.0

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

            len_fac         = parameters['len_fac']
            sma_len_fac     = parameters['sma_len_fac']
            rsi_len_fac     = parameters['rsi_len_fac']
            ema_len_fac     = parameters['ema_len_fac']
            macd_len_fac    = parameters['macd_len_fac']
            fast_multiplier = parameters['fast_multiplier']
            slow_multiplier = parameters['slow_multiplier']
            macd_multiplier = parameters['macd_multiplier']

            self.sma_fac    = parameters['sma_fac']
            self.rsi_fac    = parameters['rsi_fac']
            self.ema_fac    = parameters['ema_fac']
            self.mac_fac    = parameters['mac_fac']
            self.offset     = parameters['offset']

            self.overbought = parameters['overbought']
            self.oversold   = parameters['oversold']

            sma_length      = int(round(len_fac * sma_len_fac))
            rsi_length      = int(round(len_fac * rsi_len_fac))
            ema_length      = int(round(len_fac * ema_len_fac))
            fast_length     = int(round(len_fac * macd_len_fac * fast_multiplier))
            slow_length     = int(round(len_fac * macd_len_fac * slow_multiplier))
            macd_length     = int(round(len_fac * macd_len_fac * macd_multiplier))
            emamacd_length  = macd_length


            '''
            sma_length     = parameters['sma_length']
            ema_K          = parameters['ema_K']
            fast_K         = parameters['fast_K']
            slow_K         = parameters['slow_K']
            macd_K         = parameters['macd_K']
            emamacd_K      = parameters['emamacd_K']
            self.sma_fac   = parameters['sma_fac']
            self.rsi_fac   = parameters['rsi_fac']
            self.ema_fac   = parameters['ema_fac']
            self.mac_fac   = parameters['mac_fac']
            self.offset    = parameters['offset']
            '''

            dpprint(parameters)

 

        self.broker = broker
        self.candles = []

        # SMA Indicator - Are we in a Bull or Bear market according to 200 SMA?
        self.sma = Sma(sma_length)

        # RSI Indicator
        #self.rsi = Rsi(rsi_length,rsi_K)
        self.rsi = Rsi(rsi_length)

        # EMA Indicator - Are we in a rally or not?
        #self.ema = Ema(ema_length,ema_K)
        self.ema = Ema(ema_length)

        # MACD Indicator - Is the MACD bullish or bearish?
        # MACD = ema(close, fastLength) - ema(close, slowlength)
        #self.macd    = Macd( (fast_length,slow_length,macd_length), (fast_K,slow_K,macd_K) )
        self.macd    = Macd( (fast_length,slow_length,macd_length) )

        # emaMACD = ema(MACD, MACDLength)
        #self.emamacd = EmaMacd(MACD_LENGTH)
        #self.emamacd = Ema(emamacd_length,emamacd_K)
        self.emamacd = Ema(emamacd_length)

        dprint("Current actual parameters:")
        ppar = {}
        ppar['sma_length']     = self.sma.N
        ppar['rsi_length']     = self.rsi.N
        ppar['ema_length']     = self.ema.N
        ppar['fast_length']    = self.macd.N[0]
        ppar['slow_length']    = self.macd.N[1]
        ppar['macd_length']    = self.macd.N[2]
        ppar['emamacd_length'] = self.emamacd.N
        ppar['overbought']     = self.overbought
        ppar['oversold']       = self.oversold

        dpprint(ppar)

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

        cur_rsi = self.rsi.appendCandle(candle)
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

        self.cur_close = candle['c']

        if cur_sma == None:
            return

        if self.cur_close == None:
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

        '''
        if cur_close > cur_sma:
            #buy_entry = delta>0 and cur_rsi>self.rsi_overbought
            buy_entry = delta>self.overbought
        else:
            #buy_entry = delta>0 and cur_close>cur_ema and cur_rsi>self.rsi_overbought
            buy_entry = delta>self.overbought and cur_close>cur_ema

        if buy_entry and not self.broker.in_position:
            self.broker.buyBuyBuy(cur_close - cur_sma, cur_close) # ToDo - pass sensible value)
            #print("Current RSI: ",cur_rsi )

        if cur_close < cur_sma:
            #sell_entry = delta<0 and cur_rsi<self.rsi_oversold
            sell_entry = delta<self.oversold
        else:
            #sell_entry = delta<0 and cur_close<cur_ema and cur_rsi<self.rsi_oversold
            sell_entry = delta<self.oversold and cur_close<cur_ema

        if sell_entry and self.broker.in_position:
            self.broker.sellSellSell(cur_sma-cur_close, cur_close) # ToDo - pass sensible value)
            #print("Current RSI: ",cur_rsi )
        '''

        # ToDo : linear combination
        rel2sma = self.cur_close/cur_sma - 1
        #print("the current rel2sma is {}".format(rel2sma))

        rel2ema = self.cur_close/cur_ema - 1 
        #print("the current rel2ema is {}".format(rel2ema))

        relmacd = cur_macd/cur_emamacd - 1
        #print("the current relmacd is {}".format(relmacd))


        indicator_ = self.sma_fac*rel2sma + self.ema_fac*rel2ema + self.mac_fac*relmacd + self.rsi_fac*cur_rsi + self.offset
        #print("the current signal is {}".format(signal))

        if indicator_ < -100: indicator_ = -100
        if indicator_ >  100: indicator_ =  100

        indicator = 2/(1+math.exp(-indicator_)) - 1 

        if indicator > self.overbought:
            amount = (indicator - self.overbought)/self.overbought
            if amount > 1: amount = 1
            self.broker.buyBuyBuy(amount, self.cur_close) # ToDo - pass sensible value)

        elif indicator < self.oversold:
            amount = (indicator - self.oversold)/self.oversold
            if amount > 1: amount = 1
            self.broker.sellSellSell(amount, self.cur_close) # ToDo - pass sensible value)

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

