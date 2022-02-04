Zz# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 11:48:09 2021

@author: Admin
"""

from kiteconnect import KiteConnect
import time
import os
import datetime as dt
import numpy as np
import pandas as pd  
import talib as ta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
cwd = os.chdir("C:\\Users\\Admin\\Desktop\\kite\\my working")

os.getcwd() 

api_key = "k87m1ti1drm14ya9"
api_secret = "fd7ge8a2sd13j3sbsq921ttqyyugt9ti"
kite = KiteConnect(api_key=api_key)
print(kite.login_url()) 
#request_token = "6ZAHAku6MY4F9lCKWvMIOdA0CrN7XcrX" #Extract request token from the redirect url obtained after you authorize yourself by loggin in
#Data = kite.generate_session(request_token, api_secret=api_secret) 

#create kite trading object
#kite.set_access_token(Data["access_token"])
kite.set_access_token("WmkpWksmqyQnnKHzOOWjtFtIaRE4Py1s") 

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1
#get dump of all NSE instruments    
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)


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


def ann_ret(DF,I,colunm_name):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    dfr = DF.copy()
    dfr["cum_return"] = (1 + dfr[colunm_name]).cumprod()
    n = len(dfr)/(252*I)
    ann_ret = (dfr["cum_return"].tolist()[-1])**(1/n) - 1
    return ann_ret

def volatility(DF,I,colunm_name):
    "function to calculate annualized volatility of a trading strategy"
    dfr = DF.copy()
    vol = dfr[colunm_name].std() * np.sqrt(252*I) 
    return vol

def sharpe(DF,rf,I,colunm_name):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    dfr = DF.copy()
    sr = (ann_ret(dfr,I,colunm_name) - rf)/volatility(dfr,I,colunm_name)
    return sr

def max_dd(DF,column_name):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df[column_name]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd
#df5 = df2.iloc[0:,:6]
#df5.head()

def KPIs(m,n,df5,daily_dp):
#df5['sma9'] = df5['close'].rolling(window=m).mean()
#df5['sma16'] = df5['close'].rolling(window=n).mean()
#df5[['close', 'sma9', 'sma16']].plot(grid=True, linewidth=1, figsize=(12, 8))

    df5['sma9'] = df5['close'].rolling(window=m).mean()
    df5['sma16'] = df5['close'].rolling(window=n).mean()

    df5[['close', 'sma9', 'sma16']].plot(grid=True, linewidth=1, figsize=(12, 8))

    df5['sma9_prev_day'] = df5['sma9'].shift(1)
    df5['sma16_prev_day'] = df5['sma16'].shift(1)

    df5['signal_1'] = np.where((df5['sma9'] > df5['sma16']) 
                                & (df5['sma9_prev_day'] < df5['sma16_prev_day']), 1, 0)
    df5['signal_1'] = np.where((df5['sma9'] < df5['sma16']) 
                                & (df5['sma9_prev_day'] > df5['sma16_prev_day']), -1, df5['signal_1'])
    
    ## signal for long only

    df5['long_entry'] = (df5['sma9'] > df5['sma16']) & (df5['sma9_prev_day'] < df5['sma16_prev_day'])
    df5['long_exit'] = (df5['sma9'] < df5['sma16'])  & (df5['sma9_prev_day'] > df5['sma16_prev_day'])
                           
    df5['buy_price'] = df5.apply(lambda x : x['close'] if x['sma9'] > x['sma16'] 
                                 and x['sma9_prev_day'] < x['sma16_prev_day'] else 0, axis=1)

    df5['sell_price'] = df5.apply(lambda y : -y['close'] if y['sma9'] < y['sma16'] 
                                  and y['sma9_prev_day'] > y['sma16_prev_day'] else 0, axis=1)


     ## trade & position for both long and short 
    df5['trade_price'] = df5['buy_price'] + df5['sell_price']
    df5['trade_price']=df5['trade_price'].replace(to_replace=0, method='ffill')

    df5['position_1'] = df5['signal_1'].replace(to_replace=0, method='ffill')
    ## trade and position for long only
    df5["trade_price_long_only"] = df5['buy_price']

    df5['positions_long'] = np.nan
    df5.loc[df5.long_entry, 'positions_long'] = 1
    df5.loc[df5.long_exit, 'positions_long'] = 0 

    df5.positions_long = df5.positions_long.fillna(method='ffill')
                      

    ##  calculating returns for all three conditions 
    df5['bnh_returns'] = np.log(df5['close'] / df5['close'].shift(1))
    df5['long_short_returns'] = df5['bnh_returns'] * df5['position_1'].shift(1)
    df5["long_returns"] = df5['bnh_returns'] * df5['positions_long'].shift(1) 


    df5[['bnh_returns',"long_short_returns"]].cumsum().plot(grid=True, figsize=(12, 8))
    volatility(df5,daily_dp,"bnh_returns")
    volatility(df5,daily_dp,"long_short_returns")
    signal_count=df5["signal_1"].value_counts()
    print('Buy and hold returns: ', np.round(df5['bnh_returns'].cumsum()[-1] *100, 2),"%")
    print( "bnh_dd:", max_dd(df5,"bnh_returns") *100,"%")
    print("ann_returns_bnh:", ann_ret(df5,daily_dp, "bnh_returns")*100,"%")
    print("sharpe_bnh:",sharpe(df5, 0.05, daily_dp, "bnh_returns")) 

    print('long and short returns: ', np.round(df5['long_short_returns'].cumsum()[-1] *100, 2),"%")
    print( "long_short_dd:",max_dd(df5,"long_short_returns")* 100,"%")
    print("ann_returns_long_short:", ann_ret(df5, daily_dp, "long_short_returns")*100,"%")
    print("sharpe__long_short:",sharpe(df5, 0.05, daily_dp, "long_short_returns")) 
    print("buy_signal:",signal_count[1])
    print("sell_signal:",signal_count[-1]) 
    return df5
    

tickers = ["RELIANCE","TATASTEEL","HDFCBANK","INFY","TCS"] 
tickers_pharma=["ALKEM","CADILAHC","DRREDDY","LUPIN","TORNTPHARM","CIPLA","SUNPHARMA","AUROPHARMA",
                "GLENMARK","DIVISLAB","BIOCON"]

#dates =["22-09-2015","22-09-2018","22-09-2020","22-03-2021"]
#interval =["day","60minute"]
def get_data_KPI(Tickers):
    outdf=[]
    for ticker in Tickers:
        df5 = fetchOHLCExtended(ticker,"22-09-2015","60minute")
        #df5.reset_index()
        df5.dropna(inplace=True)
        time.sleep(0.1)
        print(ticker)
        KPIs(9, 16,df5,7)
        outdf.append(df5)
    return outdf    
z1 = get_data_KPI(tickers)         
z2 =  get_data_KPI(tickers_pharma) 

         
   
    
 
            
 
df5 = fetchOHLCExtended("ALKEM","22-09-2015","60minute")         
#KPIs(m,n,df5,daily_dp)
KPIs(9, 16, df5,7) 


