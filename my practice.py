# -*- coding: utf-8 -*-
"""
@author: Admin
"""
#from selenium import webdriver
#browser = webdriver.Chrome(executable_path='C:\\Users\\Admin\\Desktop\\kite\my working\chromedriver.exe')
#browser.get('https://kite.trade/connect/login?api_key=k87m1ti1drm14ya9&v=3')
#import os
#os.getcwd()

from kiteconnect import KiteConnect
import pandas as pd
import datetime as dt
from statsmodels.api import OLS
import numpy as np
import matplotlib.pyplot as plt 
api_key = "k87m1ti1drm14ya9"
api_secret = "fd7ge8a2sd13j3sbsq921ttqyyugt9ti"
kite = KiteConnect(api_key=api_key)
print(kite.login_url()) #use this url to manually login and authorize yourself

#generate trading session
#request_token = "mnlnW93NF7QUNOZllvz8mQpXt8WCgOkT" #Extract request token from the redirect url obtained after you authorize yourself by loggin in
#data = kite.generate_session(request_token, api_secret=api_secret)

#create kite trading object
kite.set_access_token("2knJldNpg2JXmvqQxEWwcVmWfZjxUTKa")


#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)
#instrument_df.to_csv("NSE_Instruments.csv",index=False)


def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1


def fetchOHLCExtended(ticker,inception_date, interval):
    """extracts historical data and outputs in the form of dataframe
       inception date string format - dd-mm-yyyy"""
    instrument = instrumentLookup(instrument_df,ticker)
    from_date = dt.datetime.strptime(inception_date, '%d-%m-%Y')
    to_date = dt.date.today()
    data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    while True:
        if from_date.date() >= (dt.date.today() - dt.timedelta(100)):
            data = data.append(pd.DataFrame(kite.historical_data(instrument,from_date,dt.date.today(),interval)),ignore_index=True)
            break
        else:
            to_date = from_date + dt.timedelta(100)
            data = data.append(pd.DataFrame(kite.historical_data(instrument,from_date,to_date,interval)),ignore_index=True)
            from_date = to_date
    data.set_index("date",inplace=True)
    return data

df_tata = fetchOHLCExtended("HDFC","1-1-2015","day")
df_jsw = fetchOHLCExtended("HDFCBANK","1-1-2015","day")
df_nifty = fetchOHLCExtended("NIFTY 50","1-1-2015","day") 


 
# mearging a dataframe 
df = pd.concat((df_tata["close"],df_jsw["close"],df_nifty["close"]),axis=1)
df.columns =["tata_steel","jsw_steel","nifty"]
df.index = pd.to_datetime(df.index)
(df.pct_change()).cumsum().plot(figsize = (12,8))

## OLS METHOD

model =  OLS(df["tata_steel"].iloc[:90],df["jsw_steel"].iloc[:90])
model = model.fit()
print('The hedge ratio for tata_steel and jsw_steel are', np.round(model.params[0],3))
##  scatter plot
plt.scatter(df["tata_steel"],df["jsw_steel"])
df["spread"] = df.tata_steel- model.params[0]*df.jsw_steel
df["spread"].plot()
# ADF test  
from statsmodels.tsa.stattools import adfuller
adf = adfuller(df["spread"],maxlag=1)
print(adf[0])
print(adf[4])


def stat_arb(df, lookback, std_dev):
    df['moving_average'] = df.spread.rolling(lookback).mean() 
    df['moving_std_dev'] = df.spread.rolling(lookback).std()
    # creating upper band and lower band 
    df['upper_band'] = df.moving_average + std_dev*df.moving_std_dev
    df['lower_band'] = df.moving_average - std_dev*df.moving_std_dev
    
    # conditions for long entry and exit 
    df['long_entry'] = df.spread < df.lower_band
    df['long_exit'] = df.spread >= df.moving_average
    df['positions_long'] = np.nan
    df.loc[df.long_entry, 'positions_long'] = 1
    df.loc[df.long_exit, 'positions_long'] = 0
    df.positions_long = df.positions_long.fillna(method='ffill')
    
    # conditions for short entry and exit
    df['short_entry'] = df.spread > df.upper_band
    df['short_exit'] = df.spread <= df.moving_average
    df['positions_short'] = np.nan
    df.loc[df.short_entry, 'positions_short'] = -1
    df.loc[df.short_exit, 'positions_short'] = 0
    df.positions_short = df.positions_short.fillna(method='ffill')
    ## Adding long and short positions 
    df['positions'] = df.positions_long + df.positions_short
    return df
df = stat_arb(df,lookback= 15, std_dev= 1 )

df['percentage_change'] = (df.spread - df.spread.shift(1))/(model.params[0]*df.jsw_steel + df.tata_steel)
df['strategy_returns'] = df.positions.shift(1) * df.percentage_change
df['cumulative_returns'] = (df.strategy_returns+1).cumprod()
"The total strategy returns are %.2f" % ((df['cumulative_returns'].iloc[-1]-1)*100)

s = np.mean(df['strategy_returns'])/np.std(df['strategy_returns'])*(252**0.5)
'The Sharpe Ratio %.2f' % s

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["strategy_returns"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

print("max_dd", max_dd(df))
