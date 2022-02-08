# =============================================================================
# Backtesting strategy - II : Intraday resistance breakout strategy
# =============================================================================
#import necessary library required 

import numpy as np
import pandas as pd
import copy
import time
from kiteconnect import KiteConnect
import os
import datetime as dt
 
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
#get current working directory
cwd = os.chdir("C:\\Users\\Admin\\Desktop\\kite\\my working")

os.getcwd() 
#generate required request token
api_key = "***************"
api_secret = "**************************"
kite = KiteConnect(api_key=api_key)
print(kite.login_url()) 
#request_token = "JMMfGO9RlmUW1PJCYrzmVtskauQSa5d4" #Extract request token from the redirect url obtained after you authorize yourself by loggin in
#Data = kite.generate_session(request_token, api_secret=api_secret) 

#create kite trading object
#set access token 
kite.set_access_token("2knJldNpg2JXmvqQxEWwcVmWfZjxUTKa")

#set required exchange
def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1
#get dump of all NSE instruments    
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)

# Defining functions to be used in code
def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['high']-df['low'])
    df['H-PC']=abs(df['high']-df['close'].shift(1))
    df['L-PC']=abs(df['low']-df['close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2['ATR']

def AGR(DF,colunm_name):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df[colunm_name]).cumprod()
    n = len(df)/(252*78)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF,colunm_name):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df[colunm_name].std() * np.sqrt(252*78)
    return vol

def sharpe(DF,rf,colunm_name):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (AGR(df,colunm_name) - rf)/volatility(df,colunm_name)
    return sr
    

def max_dd(DF,colunm_name):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df[colunm_name]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd
         

#defining function in order to get historical data from kite  
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

#create empty dictionary to store historical data
ohlc_intraday={}

tickers = ["BAJFINANCE","AXISBANK","ADANIENT","TATAMOTORS","TATAPOWER",
           "ASHOKLEY","M&MFIN","ITC","ZEEL","NATIONALUM","MARUTI","SAIL","HINDALCO","JINDALSTEL",
           "COALINDIA","PEL","PFC"] 
for t in tickers:
    
    ohlc_intraday[t] = fetchOHLCExtended(t,"1-07-2021","5minute")
    time.sleep(0.2) 
    

################################Backtesting####################################
#def function strg to calculate returns
def strg(ohlc_intraday):
# calculating ATR and rolling max price for each stock and consolidating this info by stock in a separate dataframe
    ohlc_dict = copy.deepcopy(ohlc_intraday)
    tickers_signal = {}
    tickers_ret = {}
    for ticker in tickers:
        print("calculating ATR and rolling max price for ",ticker)
        ohlc_dict[ticker]["ATR"] = ATR(ohlc_dict[ticker],20)
        ohlc_dict[ticker]["roll_max_cp"] = ohlc_dict[ticker]["high"].rolling(20).max()
        ohlc_dict[ticker]["roll_min_cp"] = ohlc_dict[ticker]["low"].rolling(20).min()
        ohlc_dict[ticker]["roll_max_vol"] = ohlc_dict[ticker]["volume"].rolling(20).max()
        ohlc_dict[ticker].dropna(inplace=True)
        tickers_signal[ticker] = ""
        tickers_ret[ticker] = [0]


# identifying signals and calculating daily return (stop loss factored in)
    for ticker in tickers:
        print("calculating returns for ",ticker)
        for i in range(1,len(ohlc_dict[ticker])):
            if tickers_signal[ticker] == "":
               tickers_ret[ticker].append(0)
               if ohlc_dict[ticker]["high"][i]>=ohlc_dict[ticker]["roll_max_cp"][i] and \
                  ohlc_dict[ticker]["volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                   tickers_signal[ticker] = "Buy"
               elif ohlc_dict[ticker]["low"][i]<=ohlc_dict[ticker]["roll_min_cp"][i] and \
                    ohlc_dict[ticker]["volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                     tickers_signal[ticker] = "Sell"
        
            elif tickers_signal[ticker] == "Buy":
                 if ohlc_dict[ticker]["low"][i]<ohlc_dict[ticker]["close"][i-1] - ohlc_dict[ticker]["ATR"][i-1]:
                    tickers_signal[ticker] = ""
                    tickers_ret[ticker].append(((ohlc_dict[ticker]["close"][i-1] - ohlc_dict[ticker]["ATR"][i-1])/ohlc_dict[ticker]["close"][i-1])-1)
                 elif ohlc_dict[ticker]["low"][i]<=ohlc_dict[ticker]["roll_min_cp"][i] and \
                      ohlc_dict[ticker]["volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                      tickers_signal[ticker] = "Sell"
                      tickers_ret[ticker].append((ohlc_dict[ticker]["close"][i]/ohlc_dict[ticker]["close"][i-1])-1)
                 else:
                      tickers_ret[ticker].append((ohlc_dict[ticker]["close"][i]/ohlc_dict[ticker]["close"][i-1])-1)
                
            elif tickers_signal[ticker] == "Sell":
                 if ohlc_dict[ticker]["high"][i]>ohlc_dict[ticker]["close"][i-1] + ohlc_dict[ticker]["ATR"][i-1]:
                    tickers_signal[ticker] = ""
                    tickers_ret[ticker].append((ohlc_dict[ticker]["close"][i-1]/(ohlc_dict[ticker]["close"][i-1] + ohlc_dict[ticker]["ATR"][i-1]))-1)
                 elif ohlc_dict[ticker]["high"][i]>=ohlc_dict[ticker]["roll_max_cp"][i] and \
                      ohlc_dict[ticker]["volume"][i]>1.5*ohlc_dict[ticker]["roll_max_vol"][i-1]:
                      tickers_signal[ticker] = "Buy"
                      tickers_ret[ticker].append((ohlc_dict[ticker]["close"][i-1]/ohlc_dict[ticker]["close"][i])-1)
                 else:
                      tickers_ret[ticker].append((ohlc_dict[ticker]["close"][i-1]/ohlc_dict[ticker]["close"][i])-1)
                
        ohlc_dict[ticker]["ret"] = np.array(tickers_ret[ticker])
    return ohlc_dict

## function to return dictionary from  conditions
ohlc_dict=strg(ohlc_intraday)

#calculating individual stock's KPIs
agr = {}
sharpe_ratios = {}
max_drawdown = {}
for ticker in tickers:
    print("calculating KPIs for ",ticker)      
    agr[ticker] =  AGR(ohlc_dict[ticker])
    sharpe_ratios[ticker] =  sharpe(ohlc_dict[ticker],0.025)
    max_drawdown[ticker] =  max_dd(ohlc_dict[ticker]) 

KPI_df = pd.DataFrame([agr,max_drawdown,sharpe_ratios],index=["Return","Max Drawdown","Sharpe Ratio"])      
KPI_df.T 


# calculating overall strategy's KPIs
ohlc_dict=strg(ohlc_intraday)
strategy_df = pd.DataFrame()
for ticker in tickers:
    strategy_df[ticker] = ohlc_dict[ticker]["ret"]
    
strategy_df["ret"] = strategy_df.mean(axis=1) 
strategy_df["strategy_return"] = (1+strategy_df["ret"]).cumprod()
# vizualization of strategy return 
print("Strategy Annualized Return",AGR(strategy_df,"ret")*100)
print("Strategy sharpe ratio",sharpe(strategy_df,0.025,"ret"))
print("Strategy Drawdown",max_dd(strategy_df,"ret")*100)   
# vizualization of index return
strategy_df["nifty_close"] = fetchOHLCExtended("NIFTY 50","1-07-2021","5minute")["close"]    
strategy_df["nifty_ret"] =  strategy_df["nifty_close"].pct_change()
strategy_df["nifty_return"] = (1+strategy_df["nifty_ret"]).cumprod()
#nifty kpis
print("Nifty Annualized Return",AGR(strategy_df,"nifty_ret")*100)
print("Nifty sharpe ratio",sharpe(strategy_df,0.025,"nifty_ret"))
print("Nifty Drawdown",max_dd(strategy_df,"nifty_ret")*100)   

#ploting of nifty as well as strategy returns on same plot
strategy_df[["strategy_return","nifty_return"]].plot() 

 
