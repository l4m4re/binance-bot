import websocket, json, pprint, talib, numpy
import config
import sys, time, os, time
from binance.client import Client
from binance.enums import *
#from time import strptime

SOCKET = "wss://stream.binance.com:9443/ws/thetausdt@kline_1m"

RSI_PERIOD      = 14

LEN_FAC         = 6
SMA_PERIOD      = 400
EMA_PERIOD      = LEN_FAC * 20
FAST_LENGTH     = LEN_FAC * 23 
SLOW_LENGTH     = LEN_FAC * 26
MACD_LENGTH     = LEN_FAC * 9

RSI_OVERBOUGHT  = 70
RSI_OVERSOLD    = 30


TRADE_SYMBOL    = "THETAUSD"
TRADE_QUANTITY  = 10

closes          = []
in_position     = False
live            = False
cur_close       = 0.0
date_time       = time.localtime()

client = Client(config.API_KEY, config.API_SECRET, tld='us')

# Stragegy : MACD/EMA Long Strategy
# Source   : https://www.tradingview.com/script/o97VVZNr-MACD-EMA-Long-Strategy/
# 
# //@version=2
# strategy(title="MACD/EMA Long Strategy",overlay=true,scale=scale.left)
#



def calcTrade():

    global closes, in_position, cur_close

    print('.', end='')
    sys.stdout.flush()

    np_closes = numpy.array(closes)

    """
    rsi = talib.RSI(np_closes, RSI_PERIOD)
    last_rsi = rsi[-1]
    #print("the current rsi is {}".format(last_rsi))


    if last_rsi > RSI_OVERBOUGHT:
        buyBuyBuy()
    
    if last_rsi < RSI_OVERSOLD:
        sellSellSell()
    """
 
    # SMA Indicator - Are we in a Bull or Bear market according to 200 SMA?
    sma = talib.SMA(np_closes, SMA_PERIOD)
    cur_sma = sma[-1]
    #print("the current sma is {}".format(cur_sma))


    # // EMA Indicator - Are we in a rally or not?
    ema = talib.EMA(np_closes, EMA_PERIOD)
    cur_ema = ema[-1]
    #print("the current ema is {}".format(cur_ema))


    # //MACD Indicator - Is the MACD bullish or bearish?


 
    # MACD = ema(close, fastLength) - ema(close, slowlength)
    ema1     = talib.EMA(np_closes, FAST_LENGTH)
    ema2     = talib.EMA(np_closes, SLOW_LENGTH)
    macd     = ema1 - ema2
    cur_macd = macd[-1]
    #print("the current macd is {}".format(cur_macd))

    # aMACD = ema(MACD, MACDLength)
    amacd = talib.EMA(macd, MACD_LENGTH)
    cur_amacd = amacd[-1]

    #print("the current amacd is {}".format(cur_amacd))

    # delta = MACD - aMACD
    delta = cur_macd - cur_amacd

    # 
    # // Set Buy/Sell conditions
    # 

    # 
    # buy_entry= if close>SMA
    #     delta>0
    # else
    #     delta>0 and close>EMA

    if cur_close > cur_sma:
        buy_entry = delta>0
    else:
        buy_entry = delta>0 and cur_close>cur_ema

    if buy_entry:
        buyBuyBuy()

    #     
    # strategy.entry("Buy",true , when=buy_entry)
    # 
    # alertcondition(delta, title='Long', message='MACD Bullish')
    # 
    # 


    # sell_entry = if close<SMA
    #     delta<0 
    # else
    #     delta<0 and close<EMA

    if cur_close < cur_sma:
        sell_entry = delta<0
    else:
        sell_entry = delta<0 and cur_close<cur_ema

    if sell_entry:
        sellSellSell()




    # strategy.close("Buy",when= sell_entry)
    # 
    # 
    # alertcondition(delta, title='Short', message='MACD Bearish')
    # 
    # //plot(delta, title="Delta", style=cross, color=delta>=0 ? green : red )

       



def order(side, quantity, symbol, price, order_type=ORDER_TYPE_MARKET):
    try:
        if live:

            print("LIVE: sending order:",date_time, symbol,side,quantity,price,order_type)
            #order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        else:

            print("REPLAY: sending order:",date_time, symbol,side,quantity,price,order_type)

        #print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


print_obos = True

def buyBuyBuy():

    global closes, in_position, cur_close, date_time, print_obos

    if in_position:
        print("Overbought! Sell! Sell! Sell!")
        # put binance sell logic here
        order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL, closes[-1])
        if order_succeeded:
            in_position = False
    else:
        if print_obos:
            print(date_time, "It is overbought at", cur_close, "  but we don't own any. Nothing to do.")


def sellSellSell():

    global closes, in_position, cur_close, date_time, print_obos

    if in_position:
        if print_obos:
            print(date_time, "It is oversold at", cur_close, " but you already own it, nothing to do.")
    else:
        print("Oversold! Buy! Buy! Buy!")
        # put binance buy order logic here
        order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL, closes[-1])
        if order_succeeded:
            in_position = True

    
def follow(thefile):
    '''generator function that yields new lines in a file
    '''

    global live

    # seek the end of the file
    #thefile.seek(0, os.SEEK_END)
    
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            live = True
            continue

        yield line

if __name__ == '__main__':

    #prices = client.get_all_tickers()
    #print(prices)

    #for price in prices:
    #    pprint.pprint(price)

    #info = client.get_exchange_info()
    #pprint.pprint( info )

    #info = client.get_symbol_info(TRADE_SYMBOL)
    #print( info )

    #klines = client.get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    #for kline in klines:
    #    print( kline )

    
    logfile = open("ticks1m.txt","r")
    loglines = follow(logfile)    # iterate over the generator
    for line in loglines:
        x = line.split(", ")

        cur_close = float(x[1])
        closes.append(cur_close)
        
        ts_str = x[0].split(".")
        ts = time.strptime(ts_str[0], '%Y-%m-%d %H:%M:%S')

        date_time = time.strftime("%m/%d/%Y, %H:%M:%S",ts)

        if len(closes) > SMA_PERIOD:
            calcTrade()
                
