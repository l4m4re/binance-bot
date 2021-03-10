import math, pprint
import keys, sys, os
from datetime import datetime
from binance.client import Client
from binance.enums import *
from binance.websockets import BinanceSocketManager

symbol        = 'THETAUSDT'
#symbol        = 'TFUELUSDT'

# sold at $4.339
if symbol == 'THETAUSDT':
    startstoploss = 22.50
    target        = 0.0333
    stoplossfac   = 2.50            
    breakouts     = [  # level, stoplossfac, already hit
                        (4.34, 1.21, False),
                        (2.00, 1.15, False),
                        (1.50, 1.10, False),
                    ]
    print("Start stoploss", startstoploss)

# sold at $0.140
if symbol == 'TFUELUSDT':
    startstoploss = 0.55
    target        = 0.00111
    stoplossfac   = 2.50            
    breakouts     = [  # level, stoplossfac, already hit
                        (0.16, 1.21, False),
                        (0.09, 1.15, False),
                        (0.02, 1.10, False),
                    ]
    print("Start stoploss", startstoploss)

fraction      = 0.499   # buy for fraction of usdt available at script start
live          = False


avail_usdt    = 0.0
cur_low       = startstoploss
cur_stoploss  = startstoploss
bought        = False


def getInfo(client,symbol):
    _info = client.get_symbol_info(symbol)
    #pprint.pprint( _info )
    info = {}

    info['quoteAssetPrecision']=_info['quoteAssetPrecision']

    filters = _info['filters']
    for filter in filters:

        if filter['filterType'] == 'LOT_SIZE':
            info['maxQty']   = filter['maxQty']
            info['minQty']   = filter['minQty']
            info['stepSize'] = filter['stepSize']

        elif filter['filterType'] == 'MIN_NOTIONAL':
            info['minNotional']   = filter['minNotional']

    return info


def getUsdtBalance(client):
    balance = client.get_asset_balance(asset='USDT')
    #print("USDT balance: ", balance)
   
    avail  = float(balance['free'])
    locked = float(balance['locked'])

    return avail, locked

#    amount = getAmount(client,TRADE_SYMBOL, avail_usdt, target, 0.49)
def getAmount(client,symbol,avail_usdt,price):

    info = getInfo(client,symbol)
    minimum   = float(info['minQty'])
    stepsize  = float(info['stepSize'])
    precision = int(info['quoteAssetPrecision'])

    amount = avail_usdt/price

    if amount < minimum: return 0.0

    n_stepsizes = math.floor( amount / stepsize )
    amount      = round( n_stepsizes * stepsize, precision)

    if amount < minimum: return 0.0

    return amount



def buy (client, symbol):
    global bought, fraction, avail_usdt, live

    info = getInfo(client,symbol)
    minimum   = float(info['minQty'])
    stepsize  = float(info['stepSize'])
    precision = int(info['quoteAssetPrecision'])

    quoteamount = round(avail_usdt*fraction, precision )

    if not bought:
        bought = True

        print( "ordering to buy", symbol, "for ", quoteamount, "USDT" )

        if live:
            order = client.create_order( symbol=symbol, side=SIDE_BUY,
                                              type=ORDER_TYPE_MARKET, quoteOrderQty=quoteamount)
        else:
            order = client.create_test_order( symbol=symbol, side=SIDE_BUY,
                                              type=ORDER_TYPE_MARKET, quoteOrderQty=quoteamount)

        print(order)
        
        os._exit(0)

    else:
        print("already bought")


# Taker buy means the buyer is the taker and seller is the maker.
# 
# Base asset means the quantity is expressed as the amount of coins that
# were received by the buyer (as opposed to quote asset which would be the
# amount paid by the buyer in btc/eth/usdt, depending on the market)
# 
# 'Volume' is the total amount of traded coins in the timeframe, disregarding which side is the taker
# 
# So basically to calculate maker buy volume (or taker sell, which is the same):
# 
# 'Volume' - ' Taker buy base asset volume' = ' Maker buy base asset volume'

def on_message(msg):

    global bought, client, symbol, cur_low, cur_stoploss, breakouts, stoplossfac

    #print("message type: {}".format(msg['e']))
    #pprint.pprint(msg)

    if bought: 
        print("Already bought")
        return

    # do something
    if msg['e'] == 'kline':

        #print('*', end='')
        sys.stdout.flush()

        kline = msg['k']

        is_candle_closed = kline['x']
        close            = float(kline['c'])

        for idx in range(0,len(breakouts)):
            
            level = breakouts[idx][0]
            fac   = breakouts[idx][1]
            hit   = breakouts[idx][2]

            if not hit:
                #print ("checking if below", level)

                if close < level:
                   print("breakout at", level, "hit. Adjusting fac to:", fac) 
                   stoplossfac = fac
                   breakouts[idx] = (level,fac,True)
     

        if close < cur_low:
            cur_low = close
            if cur_low * stoplossfac < cur_stoploss:
                cur_stoploss = cur_low * stoplossfac

        print('current price and stoploss:', close, cur_stoploss)

        if close > cur_stoploss:
            print('stoploss hit, buying at:', close)
            buy(client, symbol)

        if close < target:
            print('target hit, buying at: ', close)
            buy(client, symbol)


        
    elif msg['e'] == 'error':
        print ("Error message received!")
        logging.debug(msg)

if __name__ == '__main__':

    client   = Client(keys.API_KEY, keys.API_SECRET)
    bm       = BinanceSocketManager(client)
    print (bm )

    #conn_key = bm.start_kline_socket(config.TRADE_SYMBOL, on_message)
    #conn_key = bm.start_symbol_ticker_socket(config.TRADE_SYMBOL, on_message)
    conn_key = bm.start_kline_socket(symbol, on_message, interval=KLINE_INTERVAL_1MINUTE)
    #conn_key = bm.start_kline_socket(config.TRADE_SYMBOL, on_message)
    #conn_key = bm.start_kline_socket('THETAUSDT', process_message)
    print (conn_key )

    #pprint.pprint( getinfo(client, TRADE_SYMBOL) )

    avail_usdt,locked = getUsdtBalance(client)

    amount = getAmount(client,symbol, avail_usdt*fraction, target)
    print("We can buy", amount, "of", symbol, "at", target)

    amount = getAmount(client,symbol, avail_usdt*fraction, startstoploss)
    print("We can buy", amount, "of", symbol, "at", startstoploss)

    if live:
        print("Running LIVE!!!")
    else:
        print("Running test")

    bm.start()
                
    #ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    #ws.run_forever()

