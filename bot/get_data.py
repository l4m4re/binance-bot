import keys, pprint, json
from binance.client import Client

client = Client(keys.API_KEY, keys.API_SECRET)

# prices = client.get_all_tickers()

# for price in prices:
#     print(price)


# https://sammchardy.github.io/binance/2018/01/08/historical-data-download-binance.html :
# 
# The get_klines endpoint returns an array of klines in this order
# 
#   [
#     1499040000000,      # Open time                    't' 0
#     "0.01634790",       # Open                         'o' 1
#     "0.80000000",       # High                         'h' 2        
#     "0.01575800",       # Low                          'l' 3       
#     "0.01577100",       # Close                        'c' 4
#     "148976.11427815",  # Volume                       'v' 5
#     1499644799999,      # Close time                   'T' 6
#     "2434.19055334",    # Quote asset volume           'Q' 7
#     308,                # Number of trades             'n' 8
#     "1756.87402397",    # Taker buy base asset volume  'V' 9
##    "28.46694368",      # Taker buy quote asset volume 'Q' 10
#     "17928899.62484339" # Ignore
#   ]



#candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Jan, 2020", "12 Jul, 2020")
#candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 Jan, 2020", "12 Jul, 2020")
#candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 Jan, 2017", "12 Jul, 2020")

#datafile = open('../data/BTCUSDT_2021_1minutes.txt', 'w', newline='') 
#klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2021")

#datafile = open('../data/BTCUSDT_20202_1minutes.txt', 'w', newline='') 
#klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2020")

#datafile = open('../data/BTCUSDT_2021_1minutes_2.txt', 'w', newline='') 
#klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2021")

#datafile = open('../data/BTCUSDT_2017.txt', 'w', newline='') 
#klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2017", "31 Dec, 2017")

#datafile = open('../data/BTCUSDT_2018.txt', 'w', newline='') 
#klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2018", "31 Dec, 2018")

datafile = open('../data/BTCUSDT_2019.txt', 'w', newline='') 
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2019", "31 Dec, 2019")

#datafile = open('../data/BTCUSDT_2017-2020.txt', 'w', newline='') 
#klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2017", "31 Dec, 2020")

#datafile = open('../data/BTCUSDT_2019-2020.txt', 'w', newline='') 
#klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2019", "31 Dec, 2020")

for kline in klines:
    candle = {}
    candle['c'] = kline[4]
    candle['T'] = kline[6]
    candle['o'] = kline[1]
    candle['h'] = kline[2]
    candle['l'] = kline[3]
    candle['v'] = kline[5]

    close = candle['c'] 

    print("candle closed at {}".format(close))
    #print(close, file=open('ticks.txt', 'a'))
    #logging.info(str(datetime.now()) + " , " + close)
    datafile.write(json.dumps(candle) + "\n")
    #candlefile.flush()


#    pprint.pprint( candlestick )
#    candlestick[0] = candlestick[0] / 1000
#    candlestick_writer.writerow(candlestick)

datafile.close()
