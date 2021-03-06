import websocket, json, pprint, numpy, pickle, time, datetime
import config
import os
from numpy import arange
from binance.client import Client
from binance.enums import *
from twilio.rest import Client as twilio

client = Client(config.API_KEY, config.API_SECRET)
account_sid = config.account_sid
auth_token = config.auth_token
client_twilio = twilio(account_sid, auth_token)
text_list = config.text_list

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@depth20"

depthData = {"BTCUSDT":[]}

i = 0

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):

    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')
    with open('depthData.json', 'w+') as f:
        json.dump(depthData, f)

def on_message(ws, message):
    global depthData

    askDepth = 0
    bidDepth = 0
    trades = client.get_recent_trades(symbol="BTCUSDT")
    price_current = float(trades[-1]['price'])
    t = int(round(time.time(),0))
    json_message = json.loads(message)
    print(json_message)

    json_message["price"] = price_current
    json_message["time"] = t

    for item in json_message['bids']:
        quote = float(item[0])
        amount = float(item[1])
        bidDepth = bidDepth + (quote*amount)

    for item in json_message['asks']:
        quote = float(item[0])
        amount = float(item[1])
        askDepth = askDepth + (quote*amount)

    depthSpread = askDepth - bidDepth

    json_message['askDepth'] = askDepth
    json_message['bidDepth'] = bidDepth
    json_message['depthSpread'] = depthSpread
    json_message.pop('asks')
    json_message.pop('bids')
    json_message.pop('lastUpdateId')
    depthData["BTCUSDT"].append(json_message)



    print(depthData)




ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()