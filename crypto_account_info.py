import asyncio
from copra.rest import Client as RestClient


#Rest API Variables
KEY = "KEY"
SECRET = "SECRET"
PASSPHRASE = "PASSPHRASE"
BTC_ACCOUNT_ID = "ACCOUNT ID"
loop = asyncio.get_event_loop()


async def get_balance(currency_name):
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        accounts = await client.accounts()
        for account in accounts:
            if account['currency'] == currency_name:
                money_available = float(account['available'])
                print(money_available)
                accountID = account['id']
                print(accountID)
                a = await client.account_history(accountID)
                print(a)
                return money_available

async def convert_currency(from_currency, to_currency):
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        converted = client.stablecoin_conversion(from_currency, to_currency)
        return converted

async def get_history():
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        a = await client.account_history(BTC_ACCOUNT_ID)
        i = 0
        for element in a[0]:
            if element['type'] == 'match':
                if i == 0:
                    b = element['amount']
                    print(b)
                    print(element)
                    i+=1
                    return b


async def get_latest_fill_price():
    async with RestClient(loop, auth=True, key=KEY, secret=SECRET, passphrase=PASSPHRASE) as client:
        fills = await client.fills(product_id='BTC-USD')
        i=0
        for item in fills[0]:
                if i == 0:
                    print(item['price'])
                    return item['price']

#loop.run_until_complete(get_balance('BTC'))
loop.run_until_complete(get_latest_fill_price())
