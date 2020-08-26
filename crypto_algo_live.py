import asyncio
from datetime import datetime
import sys
import time
from copra.websocket import Channel, Client
import pandas as pd
import cbpro
from collections import deque
from copra.rest import Client as RestClient
import tracemalloc
tracemalloc.start()

class Tick:
    def __init__(self, tick_dict):
        self.product_id = tick_dict['product_id']
        self.best_bid = float(tick_dict['best_bid'])
        self.best_ask = float(tick_dict['best_ask'])
        self.price = float(tick_dict['price'])
        self.side = tick_dict['side']
        self.size = float(tick_dict['last_size'])
        self.time = datetime.strptime(tick_dict['time'], '%Y-%m-%dT%H:%M:%S.%fZ')

    @property
    def spread(self):
        return self.best_ask - self.best_bid

class Ticker(Client):
    ls= deque([])

    def on_message(self, message):
        if message['type'] == 'ticker' and 'time' in message:
            tick = Tick(message);
            element = [tick.time, tick.price]
            self.ls.append(element);
            print("length of deque: {}".format(len(self.ls)))
            if(len(self.ls)>1000):
                self.ls.popleft()

#Websocket Variables
product_id = 'BTC-USD'
loop = asyncio.get_event_loop()
channel = Channel('ticker', product_id)
ticker = Ticker(loop, channel);

#Rest API Variables
KEY = "INSERT API KEY"
SECRET = "INSERT SECRET API PASSCODE"
PASSPHRASE = "INSERT PASSPHRASE"
BTC_ACCOUNT_ID = "INSERT CRYPTOCURRENCY ACCOUNT ID"

def heikin_ashi(df):
    heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close'])
    heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    for i in range(len(df)):
        if i == 0:
            heikin_ashi_df.iat[0, 0] = df['open'].iloc[0]
        else:
            heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i - 1, 0] + heikin_ashi_df.iat[i - 1, 3]) / 2
    heikin_ashi_df['high'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['high']).max(axis=1)
    heikin_ashi_df['low'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['low']).min(axis=1)
    return heikin_ashi_df

async def get_balance(currency_name):
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        accounts = await client.accounts()
        for account in accounts:
            if account['currency'] == currency_name:
                money_available = float(account['available'])
                return money_available

async def bestBid():
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        orderbook = await client.order_book(product_id='BTC-USD', level=1)
        print(orderbook)
        best_bid = float(orderbook['bids'][0][0])
        return best_bid

async def bestAsk():
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        orderbook = await client.order_book(product_id='BTC-USD', level=1)
        print(orderbook)
        best_ask = float(orderbook['asks'][0][0])
        return best_ask

async def get_latest_fill_price():
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        fills = await client.fills(product_id='BTC-USD')
        i=0
        for item in fills[0]:
                if i == 0:
                    return item['price']

async def buy_bestBid():
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        orderbook = await client.order_book(product_id='BTC-USD', level=1)
        print(orderbook)
        best_bid = float(orderbook['bids'][0][0])
        client.limit_order('buy', 'BTC-USD', best_bid, get_balance('USD'))

async def sell_bestAsk():
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        orderbook = await client.order_book(product_id='BTC-USD', level=1)
        print(orderbook)
        best_ask = float(orderbook['asks'][0][0])
        client.limit_order('sell', 'BTC-USD', best_ask, get_balance('BTC'))

async def say(what, when):
    while len(what) == 0:
        await asyncio.sleep(when)
        print("waiting...")
    while True:
        await asyncio.sleep(when)
        print("processing deque...{}".format(len(what)))
        dlist=list(what) # convert deque back to a list
        temp_1 = pd.DataFrame(data=dlist, columns=["time", "price"])
        temp_1['Datetime'] = pd.to_datetime(temp_1['time'])
        temp_1 = temp_1.set_index('Datetime')
        temp_2 = temp_1.drop(columns=['time'])
        df = temp_2.resample('1Min').ohlc()
        df.columns = ['open', 'high', 'low', 'close']  # rename the columns for heikin_ashi() below
        if len(df.index) <= 5:
            await asyncio.sleep(5)
        else:
            ha = heikin_ashi(df)
            print(ha)
            if ha.iloc[len(df.index)-4,0] > ha.iloc[len(df.index)-4,3] \
                    and ha.iloc[len(df.index)-3,0] < df.iloc[len(df.index)-3,3] \
                    and ha.iloc[len(df.index)-2,0] < df.iloc[len(df.index)-2,3] \
                    and ha.iloc[len(df.index)-1,0] < df.iloc[len(df.index)-1,3]\
                    and await get_balance('USD') > 0 \
                    and await bestBid() <= (await get_latest_fill_price())*0.99:
                await buy_bestBid()
            elif ha.iloc[len(df.index)-4,0] < ha.iloc[len(df.index)-4,3] \
                    and ha.iloc[len(df.index)-3,0] > df.iloc[len(df.index)-3,3] \
                    and ha.iloc[len(df.index)-2,0] > df.iloc[len(df.index)-2,3] \
                    and ha.iloc[len(df.index)-1,0] > df.iloc[len(df.index)-1,3]\
                    and await get_balance('BTC') > 0 \
                    and await bestAsk() >= (await get_latest_fill_price())*1.01:
                await sell_bestAsk()
            else:
                print("hold")

loop.create_task(say(ticker.ls, 1))

try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(ticker.close())
    loop.close()
