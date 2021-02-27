import websocket, json, pprint
import config, sys, logging
from datetime import datetime

SOCKET = "wss://stream.binance.com:9443/ws/thetausdt@kline_1m"

logging.basicConfig(filename='ticks1m.txt', level=logging.DEBUG, format='')

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    
    #print('received message')
    print('.', end='')
    sys.stdout.flush()

    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        #print(close, file=open('ticks.txt', 'a'))
        logging.info(str(datetime.now()) + " , " + close)

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
