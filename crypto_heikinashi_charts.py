import asyncio
from datetime import datetime
from copra.websocket import Channel, Client
import pandas as pd
from collections import deque
from copra.rest import Client as RestClient
import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc

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
            if(len(self.ls)>2000):
                self.ls.popleft()


product_id = 'BTC-USD'
loop = asyncio.get_event_loop()
channel = Channel('ticker', product_id)
ticker = Ticker(loop, channel);

async def get_order_book():
    async with RestClient(loop) as rest_client:
        orderbook=await rest_client.order_book(product_id="BTC-USD", level=1)
        bids=orderbook['bids']
        print(bids[0][0])
        print(bids[0][1])

async def say(what, when, ax2):

    while len(what) == 0:
        await asyncio.sleep(when)
        print("waiting...")

    while True:
        await asyncio.sleep(when)
        await get_order_book()

        print("processing deque...{}".format(len(what)))
        dlist=list(what)
        temp_1 = pd.DataFrame(data=dlist, columns=["time", "price"])
        temp_1['Datetime'] = pd.to_datetime(temp_1['time'])
        temp_1 = temp_1.set_index('Datetime')
        temp_2 = temp_1.drop(columns=['time'])
        df = temp_2.resample('1Min').ohlc()
        df.columns = ['open', 'high', 'low', 'close']
        ax2.set_xlim(left=-1, right=50)
        ax2.set_ylim(bottom=df['low'].min()-25, top=df['high'].max()+25)

        if len(df.index) <= 1:
            await asyncio.sleep(5)
        else:
            ha = heikin_ashi(df)
            candlestick2_ohlc(ax2, ha['open'], ha['high'], ha['low'], ha['close'], width=0.5, colorup='g',
                              colordown='r',
                              alpha=1.0)
        plt.pause(0.1)
        ax2.clear()

fig,(ax2) = plt.subplots(nrows=1,ncols=1)
fig.suptitle('BTC-USD Candlestick Chart', fontsize=12)
ax2.grid(False)
plt.xlabel('Time', fontsize=10)
plt.ylabel('Price(USD)', fontsize=10)

loop.create_task(say(ticker.ls, 5, ax2))

try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(ticker.close())
    loop.close()
