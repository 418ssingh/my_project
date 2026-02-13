# -*- coding: utf-8 -*-
"""
@author: Admin
"""


from kiteconnect import KiteConnect
from selenium import webdriver
import time
import os
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt 


api_key = "k87m1ti1drm14ya9"
api_secret = "fd7ge8a2sd13j3sbsq921ttqyyugt9ti"
kite = KiteConnect(api_key=api_key)
print(kite.login_url())

#request_token = "n3D0mgij03MDV1K95siBYTFzWFVdlUoc" #Extract request token from the redirect url obtained after you authorize yourself by loggin in
#Data = kite.generate_session(request_token, api_secret=api_secret)

#create kite trading object
#kite.set_access_token(Data["access_token"])
kite.set_access_token("DeEh3leNffz54he5jGJNx2yebPLipcvB")


#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)
#instrument_df.to_csv("NSE_Instruments_31122019.csv",index=False)


def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1



import numpy as np
import pandas as pd  
import statistics
from datetime import datetime
import talib as ta
import matplotlib.pyplot as plt
import yfinance as yf
import datetime
import warnings
warnings.filterwarnings('ignore')

def calc_rsi(df,rsi):
    difference=df["close"].diff()
    difference=difference[1:]
    up,down=difference.clip(lower=0), difference.clip(upper=0)
    roll_up = up.rolling(rsi).mean()
    roll_down = down.abs().rolling(rsi).mean()
    MAR = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + MAR))
    df["RSI"]=RSI
    #df["sma"]=df["sma"].shift(1)
    df["RSI"]=df["RSI"].shift(1)
    return df
    
    
def bbands(close,period,bar):
    upper,middle,lower=ta.BBANDS(close.values,timeperiod=period,nbdevup=bar, nbdevdn=bar,matype=0)
    return upper,middle,lower


def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(252*25)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["ret"].std() * np.sqrt(252*25)
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr
    

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

def calc_drawdown(cum_rets):
    # Calculate the running maximum
    running_max = np.maximum.accumulate(cum_rets.dropna())
    # Ensure the value never drops below 1
    running_max[running_max < 1] = 1
    # Calculate the percentage drawdown
    drawdown = (cum_rets)/running_max - 1
    return drawdown

def max_dd(DF,column_name):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df[column_name]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

def max_dd_bnh(DF,column_name):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df[column_name]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

tickers = ["INFY","WIPRO","HCLTECH","LTI","DRREDDY","NESTLEIND","LALPATHLAB","SUNPHARMA",
           "GLAND","GLENMARK","CIPLA","VOLTAS","GRASIM","ITC","HINDUNILVR","TATASTEEL",
           "JSWSTEEL","BPCL","RELIANCE","HDFCBANK","HDFC","ADANIENT","ADANIPORTS",
           "UPL","HINDALCO"]

data_capture ={"INFY":0,"WIPRO":0,"HCLTECH":0,"LTI":0,"DRREDDY":0,"NESTLEIND":0,"LALPATHLAB":0,
               "SUNPHARMA":0,"GLAND":0,"GLENMARK":0,"CIPLA":0,"VOLTAS":0,"GRASIM":0,"ITC":0,
               "HINDUNILVR":0,"TATASTEEL":0,"JSWSTEL":0,"BPCL":0,"RELIANCE":0,"HDFCBANK":0,
               "HDFC":0,"ADANIENT":0,"ADANIPORTS":0,"UPL":0,"HINDALCO":0}

def fetchOHLC(ticker,interval,duration):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrumentLookup(instrument_df,ticker)
    data = pd.DataFrame(kite.historical_data(instrument,dt.date.today()-dt.timedelta(duration), dt.date.today(),interval))
    data.set_index("date",inplace=True)
    return data

#defining function in order to get historical data from kitefrom particular date
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
#can be used to make dictionary of all required tickers,using fetchOHLCExtended
#for t in tickers:
    #data_capture2[t] = fetchOHLCExtended(t,'%d-%m-%Y',"15minute")

#with fetchOHLC function 
data_capture["INFY"] = fetchOHLC("INFY","15minute",200) 
data_capture["WIPRO"] = fetchOHLC("WIPRO","15minute",200) 
data_capture["HCLTECH"] = fetchOHLC("HCLTECH","15minute",200)
data_capture["LTI"] = fetchOHLC("LTI","15minute",200)

data_capture["DRREDDY"] = fetchOHLC("DRREDDY","15minute",200)
data_capture["NESTLEIND"] = fetchOHLC("NESTLEIND","15minute",200)
data_capture["LALPATHLAB"] = fetchOHLC("LALPATHLAB","15minute",200) 
data_capture["SUNPHARMA"] = fetchOHLC("SUNPHARMA","15minute",200)
data_capture["GLAND"] = fetchOHLC("GLAND","15minute",200) 
data_capture["GLENMARK"] = fetchOHLC("GLENMARK","15minute",200)
data_capture["CIPLA"] = fetchOHLC("CIPLA","15minute",200) 

data_capture["VOLTAS"] = fetchOHLC("VOLTAS","15minute",200)
data_capture["GRASIM"] = fetchOHLC("GRASIM","15minute",200)
data_capture["ITC"] = fetchOHLC("ITC","15minute",200)
data_capture["HINDUNILVR"] = fetchOHLC("HINDUNILVR","15minute",200)
data_capture["TATASTEEL"] = fetchOHLC("TATASTEEL","15minute",200)
data_capture["JSWSTEEL"] = fetchOHLC("JSWSTEEL","15minute",200)
data_capture["BPCL"] = fetchOHLC("BPCL","15minute",200)
data_capture["RELIANCE"] = fetchOHLC("RELIANCE","15minute",200)

data_capture["HDFCBANK"] = fetchOHLC("HDFCBANK","15minute",200)
data_capture["HDFC"] = fetchOHLC("HDFC","15minute",200)
data_capture["ADANIENT"] = fetchOHLC("ADANIENT","15minute",200)
data_capture["ADANIPORTS"] = fetchOHLC("ADANIPORTS","15minute",200)
data_capture["UPL"] = fetchOHLC("UPL","15minute",200)
data_capture["HINDALCO"] = fetchOHLC("HINDALCO","15minute",200)

#d1 = fetchOHLC("ASIANPAINT","15minute", 200)
data = data_capture["INFY"] 
#data= data_capture["WIPRO"]
#data = data_capture["HCLTECH"] 
#data = data_capture["HCLTECH"]
#data= data_capture["LTI"] 

#data= data_capture["DRREDDY"]
#data= data_capture["NESTLEIND"] 
#data = data_capture["LALPATHLAB"] 
#data=data_capture["SUNPHARMA"] 
#data = data_capture["GLAND"] 
#data = data_capture["GLENMARK"]
#data= data_capture["CIPLA"]

#data= data_capture["VOLTAS"] 
#data= data_capture["GRASIM"] 
#data= data_capture["ITC"] 
#data=data_capture["HINDUNILVR"] 
#data=data_capture["TATASTEEL"]
#data= data_capture["JSWSTEEL"] 
#data=data_capture["BPCL"] 
#data= data_capture["RELIANCE"] 

#data = data_capture["HDFCBANK"] 
#data = data_capture["HDFC"]
#data = data_capture["ADANIENT"]
#data = data_capture["ADANIPORTS"]  
#data= data_capture["UPL"] 
#data = data_capture["HINDALCO"] 

rsi=2
rsi_up=70
rsi_down=30
sma=20
commission=0.01
stdev_win=20
std_dev_factor=2
fastperiod=3
slowperiod=10
sl_per=10/100

data=calc_rsi(data,rsi)
data["sma"]=data["close"].rolling(sma).mean()

data["upper"],data["middle"],data["lower"]=bbands(data["close"], stdev_win, std_dev_factor)
data["ACCDist"]=ta.ADOSC(data["high"],data["low"],data["close"],data["volume"],fastperiod=fastperiod,slowperiod=slowperiod)
data["Price"]=data["close"]
data["signal"]=0
data["sqoff"]=0
entry_b=0
entry_s=0


for i,value in data.iloc[(sma+5):].iterrows():
    t=i
    loc=data.index.get_loc(t)
    #Bear entry
    if(data["signal"][loc-1]==0 
       and data["RSI"][loc-2]>rsi_up and data["high"][loc-2]>data["upper"][loc-2] 
       and data["RSI"][loc-1]<data["RSI"][loc-2] and data["high"][loc-1]>data["high"][loc-2] and data["ACCDist"][loc-1]<data["ACCDist"][loc-2] 
       and data["low"][loc]<data["low"][loc-1]):
        entry_s=entry_s+1
        data["signal"][loc]=-1
        data["Price"][loc]=(data["close"][loc])-((data["close"][loc]*commission)/100)
        sl_price_buy = data["high"][loc]+(data["high"][loc]*sl_per)
    elif(data["signal"][loc-1]==-1 and data["high"][loc]>sl_price_buy):
        data["signal"][loc]=0
        data["Price"][loc]=(data["close"][loc])+((data["close"][loc]*commission)/100)
        data["sqoff"][loc]=1
    elif(data["signal"][loc-1]==-1 and data["low"][loc]<data["sma"][loc]):
        data["signal"][loc]=0
        data["Price"][loc]=(data["close"][loc])+((data["close"][loc]*commission)/100)
        
    #Bull entry
    elif(data["signal"][loc-1]==0 
       and data["RSI"][loc-2]<rsi_down and data["low"][loc-2]<data["lower"][loc-2] 
       and data["RSI"][loc-1]>data["RSI"][loc-2] and data["low"][loc-1]<data["low"][loc-2] and data["ACCDist"][loc-1]>data["ACCDist"][loc-2] 
       and data["high"][loc]>data["high"][loc-1]):
        entry_b=entry_b+1
        data["signal"][loc]=1
        data["Price"][loc]=(data["close"][loc])+((data["close"][loc]*commission)/100)
        sl_price_sell = data["low"][loc]-(data["low"][loc]*sl_per)
    elif(data["signal"][loc-1]==1 and data["low"][loc]<sl_price_sell):
        data["signal"][loc]=0
        data["Price"][loc]=(data["close"][loc])-((data["close"][loc]*commission)/100)
        data["sqoff"][loc]=1
    elif(data["signal"][loc-1]==1 and data["high"][loc]>data["sma"][loc]):
        data["signal"][loc]=0
        data["Price"][loc]=(data["close"][loc])-((data["close"][loc]*commission)/100)
        
    else:
        data["signal"][loc]=data["signal"][loc-1]

        
data["signal_shift"]=data['signal'].shift(1)
data["pct_change"]=data["Price"].pct_change()
data['strategy_returns'] = data['pct_change'] * data['signal'].shift(1)
data['bnh']=(data['pct_change']+1).cumprod()-1
data['c_s_ret']=(data['strategy_returns']+1).cumprod()-1
print("Total buy entries:",entry_b)
print("Total sell entries:",entry_s)
print("Strat returns:",data["c_s_ret"][-1]*100)
print("BNH returns:",data["bnh"][-1]*100)
print("BNH Drawdowns:",max_dd_bnh(data, "pct_change")*100)
print("Strat max-drawdown:",max_dd(data,"strategy_returns")*100)

