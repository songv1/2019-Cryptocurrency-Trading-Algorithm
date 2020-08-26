# Cryptocurrency Trading Algorithm
This project is a humble attempt at a trading algorithm using the Heikin-Ashi indicator. In addition to the live trading algorithm, other files in this project include code for data visualization and backtesting. 

# Motivation
I had some experience with data science from my research internship with the Yale Department of Astronomy and wanted to apply that knowledge to trading cryptocurrency on my CoinbasePro account. This project was my first foray into algorithmic trading.

# Disclaimer
It may be more profitable to trade by hand on CoinbasePro rather than using this particular algorithm. I largely attribute this observation to CoinbasePro's trading fees, which can be quite costly to small traders. If you can bypass the fees, this algorithm may work out well. The Heikin-Ashi technique should be most profitable during times of high price volatility. 

Moreover, the Heikin-Ashi technique is a backwards-looking trading strategy. In order to predict the next trade, you have to look at what happened a few candlesticks back. That being said, it's also kind of slow because you can't form a candlestick without waiting for more data to come through. If you trade too early (i.e. without getting the buy/sell signal from consecutive positive/negative candlesticks), you risk buying/selling on a false trend. If you trade too late (i.e. waiting too long for consecutive candlesticks to form) then you risk buying at the peak or selling at the valley, and we all know a successful trader should buy low and sell high. Not the other way around!

On the other hand, the Heikin-Ashi indicator still has an advantage over the regular candlestick since Heikin-Ashi essentially takes the average of the price movement at any given tick. This presents upwards/downwards trends more clearly. The Heikin-Ashi technique can be implemented successfully if you buy at the end of a downward trend and sell at the end of an upward trend. 

This Investopedia [article](https://www.investopedia.com/trading/heikin-ashi-better-candlestick/#:~:text=Heikin%2DAshi%2C%20also%20sometimes%20spelled,trends%20and%20predict%20future%20prices.) by Justin Kuepper gives a detailed overview of how Heikin-Ashi can be used in trading. 

It would be interesting to see how effective Heikin-Ashi is in HFT compared to more long-term trading actions. 

# Project Description
Make sure all necessary packages, clients, and software are installed before running.

* **crypto_candlestick_charts.ipynb** This program initiates a public client. Using information from CoinbasePro, this program retrieves the historic candlestick data of a specified product (e.g. BTC-USD) and saves it as a .csv file. Candlestick and Heikin-Ashi Candlestick graphs are produced from the .csv data.  

* **crypto_account_info.py** Retrieves basic information from a specified CoinbasePro account. 

* **crypto_heikinashi_charts.py** Produces a live candlestick chart of a specified product. 

* **crypto_backtest.py** A backtest for the Heikin-Ashi trading algorithm. Users must input valid entries for websocket variables and Rest API variables. 

* **crypto_algo_live.py** The live trading algorithm. Users must input valid entries for websocket variables and Rest API variables. 

# Screenshots

![BTC Candlestick Chart](/Users/victoriasong/Desktop/Github/Crypto\Trading\Algo\2019/bitoinCandleChart.png )

![Bitcoin Heikin-Ashi Candlestick Chart](/Users/victoriasong/Desktop/Github/Crypto\Trading\Algo\2019/bitcoinCandleHA.png)

# Installation 
Two different python clients were used for this project. More information about their usages can be found on the respective pages.  
* [copra](https://github.com/tpodlaski/copra) by tpodlaski
* [cbpro](https://github.com/danpaquin/coinbasepro-python) by dan-paquin

You will also need packages that can be found in the Anaconda Distribution, as well as mplfinance. 

# API Reference
I used the CoinbasePro API found [here](https://docs.pro.coinbase.com/).

# Acknowledgements
I would like to thank...
* Justin Kuepper for writing an article about the Heikin-Ashi method, which provided invaluable information for the backbone of this project. 
* Tony Podlaski and Daniel Paquin for providing these python clients to the public.
* I would like to thank the Coinbase team for providing a trading platform dedicated to cryptocurrencies. 

# License
MIT © Victoria Song
