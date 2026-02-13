# -*- coding: utf-8 -*-
"""
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

api_key = "**************"
api_secret = "*******************"
kite = KiteConnect(api_key=api_key)
print(kite.login_url()) 
request_token = "SWdk1bWo3HfqoymBOb0eta2OZoKpYSqJ" #Extract request token from the redirect url obtained after you authorize yourself by loggin in
Data = kite.generate_session(request_token, api_secret=api_secret) 

#create kite trading object
#kite.set_access_token(Data["access_token"])
kite.set_access_token("68xWbHQcjU95ZwN0SDYtvEQfEKgCKOqm") 

tickers_IT = ["INFY","WIPRO","HCLTECH","LTI","OFSS","MPHASIS","TECHM",'MINDTREE',"COFORGE"]

tickers_pharma =["ALKEM","CADILAHC","DRREDDY","LUPIN","TORNTPHARM","CIPLA","SUNPHARMA","AUROPHARMA",
           "GLENMARK","DIVISLAB","BIOCON"]

tickers_bank =["IDFCFIRSTB","SBIN","KOTAKBANK","INDUSINDBK","PNB",
           "ICICIBANK","HDFCBANK","AXISBANK","FEDERALBNK","AUBANK","BANDHANBNK","RBLBANK"] 

tickers_finserv =["PFC","BAJAJFINSV","ICICIGI","SBIN","KOTAKBANK","HDFC","ICICIBANK",
                  "PEL","RECLTD","M&MFIN","BAJFINANCE","MUTHOOTFIN","HDFCBANK","AXISBANK",
                  "HDFCAMC","HDFCLIFE","SRTRANSFIN","CHOLAFIN","ICICIPRULI","SBILIFE"] 

tickers_fmcg = ["EMAMILTD","PGHH","NESTLEIND","MARICO","VBL","COLPAL","JUBLFOOD",
                "MCDOWELL-N","ITC","UBL","BRITANNIA","HINDUNILVR","GODREJCP","DABUR",
                "TATACONSUM"] 

tickers_auto = ["ASHOKLEY","TATAMOTORS","EICHERMOT","BOSCHLTD","MARUTI","HEROMOTOCO",
                "AMARAJABAT","BHARATFORG","MRF","M&M","TVSMOTOR","BAJAJ-AUTO","EXIDEIND",
                "BALKRISIND","TIINDIA"] 

tickers_energy = ["ONGC","NTPC","BPCL","POWERGRID","IOC", "GAIL","RELIANCE","HINDPETRO",
                  "TATAPOWER"]

tickers_media = ["DISHTV","ZEEL","PVR","SUNTV","DBCORP","INOXLEISUR","TV18BRDCST","NETWORK18",
                 "TVTODAY","JAGRAN"]

tickers_metal = ["WELCORP","APLAPOLLO","SAIL","HINDALCO","TATASTEEL","NATIONALUM","JINDALSTEL",
                 "VEDL","JSWSTEEL","RATNAMANI","NMDC","HINDZINC","COALINDIA","ADANIENT","MOIL"]

tickers_realty = ["GODREJPROP","PHOENIXLTD","OBEROIRLTY","DLF","SUNTECK","HEMIPROP","BRIGADE",
                  "SOBHA","IBREALEST","PRESTIGE"]

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1
#get dump of all NSE instruments    
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)

#function to fetch data from kite
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

data_capture_IT ={"INFY":0,"WIPRO":0,"HCLTECH":0,"LTI":0,"OFSS":0,"MPHASIS":0,
               "TECHM":0,"MINDTREE":0,"COFORGE":0} 

data_capture_pharma = {"ALKEM":0,"CADILAHC":0,"DRREDDY":0,"LUPIN":0,"TORNTPHARM":0,
                       "CIPLA":0,"SUNPHARMA":0,"AUROPHARMA":0,"GLENMARK":0,"DIVISLAB":0,"BIOCON":0}

data_capture_bank ={"IDFCFIRSTB":0,"SBIN":0,"KOTAKBANK":0,"INDUSINDBK":0,"PNB":0,
           "ICICIBANK":0,"HDFCBANK":0,"AXISBANK":0,"FEDERALBNK":0,"AUBANK":0,
           "BANDHANBNK":0,"RBLBANK":0}
data_capture_finserv ={"PFC":0,"BAJAJFINSV":0,"ICICIGI":0,"SBIN":0,"KOTAKBANK":0,"HDFC":0,
                       "ICICIBANK":0,"PEL":0,"RECLTD":0,"M&MFIN":0,"BAJFINANCE":0,"MUTHOOTFIN":0,"HDFCBANK":0,
                  "AXISBANK":0,"HDFCAMC":0,"HDFCLIFE":0,"SRTRANSFIN":0,"CHOLAFIN":0,"ICICIPRULI":0,"SBILIFE":0}

data_capture_fmcg ={"EMAMILTD":0,"PGHH":0,"NESTLEIND":0,"MARICO":0,"VBL":0,"COLPAL":0,
                    "JUBLFOOD":0,"MCDOWELL-N":0,"ITC":0,"UBL":0,"BRITANNIA":0,"HINDUNILVR":0,
                    "GODREJCP":0,"DABUR":0,"TATACONSUM":0} 
data_capture_auto = {"ASHOKLEY":0,"TATAMOTORS":0,"EICHERMOT":0,"BOSCHLTD":0,"MARUTI":0,
                     "HEROMOTOCO":0,"AMARAJABAT":0,"BHARATFORG":0,"MRF":0,"M&M":0,"TVSMOTOR":0,
                     "BAJAJ-AUTO":0,"EXIDEIND":0,"BALKRISIND":0,"TIINDIA":0}
data_capture_energy ={"ONGC":0,"NTPC":0,"BPCL":0,"POWERGRID":0,"IOC":0, "GAIL":0,
                      "RELIANCE":0,"HINDPETRO":0,"TATAPOWER":0}

data_capture_media ={"DISHTV":0,"ZEEL":0,"PVR":0,"SUNTV":0,"DBCORP":0,"INOXLEISUR":0,
                     "TV18BRDCST":0,"NETWORK18":0,"TVTODAY":0,"JAGRAN":0}
data_capture_metal ={"WELCORP":0,"APLAPOLLO":0,"SAIL":0,"HINDALCO":0,"TATASTEEL":0,
                     "NATIONALUM":0,"JINDALSTEL":0,"VEDL":0,"JSWSTEEL":0,"RATNAMANI":0,
                     "NMDC":0,"HINDZINC":0,"COALINDIA":0,"ADANIENT":0,"MOIL":0} 

data_capture_realty ={"GODREJPROP":0,"PHOENIXLTD":0,"OBEROIRLTY":0,"DLF":0,"SUNTECK":0,
                      "HEMIPROP":0,"BRIGADE":0,"SOBHA":0,"IBREALEST":0,"PRESTIGE":0}


def fetch_data(i,tickr,sector,inception_date):
    for t in tickr:
        sector[t] = fetchOHLCExtended(t,inception_date,i) 
        time.sleep(0.2) 
    return sector 
  
#fetch_data("15minute",tickers_bank,data_capture_bank,200) 
#fetch_data("15minute",tickers_pharma,data_capture_pharma,200)
#fetch_data("60minute", tickers_bank,data_capture_bank,200) 


# Function to compute annualized returns
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

def max_dd_bnh(DF,column_name):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df[column_name]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

def lrsi(data,gamma):
    data["Price"]=data["close"]
    data["l0"]=0
    data["l1"]=0
    data["l2"]=0
    data["l3"]=0
    data["l0"][0]=data["Price"][0]
    data["l1"][0]=data["Price"][0]
    data["l2"][0]=data["Price"][0]
    data["l3"][0]=data["Price"][0]
    
    
    
    for i in range(1,len(data)):
        data["l0"][i] = (1 - gamma) * data["Price"][i] + gamma * data["l0"][i-1]
        data["l1"][i] = -gamma *data["l0"][i] + data["l0"][i-1] + gamma * data["l1"][i-1]
        data["l2"][i] = -gamma * data["l1"][i] + data["l1"][i-1] + gamma * data["l2"][i-1]
        data["l3"][i] = -gamma * data["l2"][i] + data["l2"][i-1] + gamma * data["l3"][i-1]
        
    data["cu"]=0
    data["cd"]=0
    for i in range(1,len(data)):
        if(data["l0"][i]>=data["l1"][i]):
            data["cu"][i]=data["l0"][i]-data["l1"][i]
        else:
            data["cd"][i]=data["l1"][i]-data["l0"][i]
        
        if(data["l1"][i]>=data["l2"][i]):
            data["cu"][i]=data["cu"][i]+data["l1"][i]-data["l2"][i]
        else:
            data["cd"][i]=data["cd"][i]+data["l2"][i]-data["l1"][i]
        
        if(data["l2"][i]>=data["l3"][i]):
            data["cu"][i]=data["cu"][i]+data["l2"][i]-data["l3"][i]
        else:
            data["cd"][i]=data["cd"][i]+data["l3"][i]-data["l2"][i]
        
        
    data["lrsi"]=np.where(data["cu"]+data["cd"]!=0,data["cu"]/(data["cu"]+data["cd"]),0)
    
    return data
    
def backtest(data,parameters):
    #sma,emal,emas,lrsiup,lrsidown,sl%,rsi_period,rsibull,rsibear,commission%
    #parameters=[200,50,20,[0.20,0.40],[0.60,0.80],3,14,20,70,0.07]
    sma=parameters[0]
    emal=parameters[1]
    emas=parameters[2]
    lrsiup=parameters[3]
    lrsidown=parameters[4]
    sl_per=parameters[5]
    rsi_period=parameters[6]
    rsi_bull=parameters[7]
    rsi_bear=parameters[8]
    commission=parameters[9]
    
    data["sma"]=data["close"].rolling(window=sma).mean()
    data["emal"]=data["close"].ewm(span=emal, adjust=False).mean()
    data["emas"]=data["close"].ewm(span=emas, adjust=False).mean()
    data["Price"]=data["close"]
    data["RSI"]=ta.RSI(data["close"],timeperiod=rsi_period)
    entry_b=0
    entry_s=0
    data["signal"]=0
    data["sl"]=0
    
    for i,value in data.iloc[(sma):].iterrows():
        t=i
        loc=data.index.get_loc(t)
        
        #Bullish
        if(data["signal"][loc-1]==0 and data["close"][loc-1]>data["sma"][loc-1] and data["close"][loc-1]<data["emal"][loc-1] and data["close"][loc-1]<data["emas"][loc]-1 and lrsiup[0]<data["lrsi"][loc-1]<lrsiup[1]):
            data["signal"][loc]=1
            entry_b=entry_b+1
            data["Price"][loc]=(data["open"][loc])+((data["open"][loc]*commission)/100)
            sl=data["low"][loc-1]-(data["low"][loc-1]*sl_per/100)
            data["sl"][loc]=sl
            
        elif(data["signal"][loc-1]==1 and data["low"][loc]<sl):
            data["signal"][loc]=0
            data["Price"][loc]=(data["close"][loc])-((data["close"][loc]*commission)/100)
            data["sl"][loc]=sl
        elif(data["signal"][loc-1]==1 and data["RSI"][loc]>rsi_bull):
            data["signal"][loc]=0
            data["Price"][loc]=(data["close"][loc])-((data["close"][loc]*commission)/100) 
            
            
        #Bear entry
        elif(data["signal"][loc-1]==0 and data["close"][loc-1]<data["sma"][loc-1] and data["close"][loc-1]>data["emal"][loc-1] and data["close"][loc-1]>data["emas"][loc]-1 and lrsidown[0]<data["lrsi"][loc-1]<lrsidown[1]):
            data["signal"][loc]=-1
            entry_s=entry_s+1
            data["Price"][loc]=(data["open"][loc])+((data["open"][loc]*commission)/100)
            sl=data["high"][loc-1]+(data["high"][loc-1]*sl_per/100)
            
            data["sl"][loc]=sl
            
        elif(data["signal"][loc-1]==-1 and data["high"][loc]>sl):
            data["signal"][loc]=0
            data["Price"][loc]=(data["close"][loc])+((data["close"][loc]*commission)/100)
            data["sl"][loc]=sl
        elif(data["signal"][loc-1]==-1 and data["RSI"][loc]<rsi_bear):
            data["signal"][loc]=0
            data["Price"][loc]=(data["close"][loc])+((data["close"][loc]*commission)/100) 
            
        else:
            data["signal"][loc]=data["signal"][loc-1]
        
    data["signal_shift"]=data['signal'].shift(1)
    data["pct_change"]=data["Price"].pct_change()
    data['strategy_returns'] = data['pct_change'] * data['signal'].shift(1)
    data['bnh']=(data['pct_change']+1).cumprod()-1
    data['c_s_ret']=(data['strategy_returns']+1).cumprod()-1
    data["total_entry_b"] = entry_b
    data["total_entry_s"] = entry_s
    #print(sma,emal,emas,lrsiup,lrsidown,sl_per,rsi_period,rsi_bull,rsi_bear,commission)
    print("Total buy entries:",entry_b)
    print("Total sell entries:",entry_s)
    print("Strat returns:",data["c_s_ret"][-1]*100)
    print("BNH returns:",data["bnh"][-1]*100)
    print("Drawdown:",max_dd(data, "strategy_returns")*100)
    print("BNH drawdown: ",max_dd_bnh(data, "pct_change")*100)
        
    return data 

def KPI(intval,d_p_day,tickers_sector,data_capture_sector,gamma,parameters,inception_date):
    print("downloading data for stocks")
    fetch_data(intval,tickers_sector,data_capture_sector,inception_date)
    ann_ret_str ={} 
    ann_ret_bnh = {}
    sharpe_strategy ={}
    sharpe_bnh = {}
    drawdown_strategy ={}
    drawdown_bnh ={} 
    #returns and buy and sell entries
    Total_buy_entries ={}
    Total_sell_entries ={}
    Strat_returns ={}
    BNH_returns={}

    for ticker in tickers_sector:
        #print("calculating returns drawdown no of position",ticker)
        df = data_capture_sector[ticker]
        df=lrsi(df,gamma)
        #sma,emal,emas,lrsiup,lrsidown,sl%,tp%,commission%
        #parameters=[200,50,20,[0.20,0.40],[0.60,0.80],3,14,20,70,0.01]
        df=backtest(df,parameters)
        
        
        #print("plotting_charts for",ticker)
        #df[["c_s_ret","bnh"]].plot()
        #plt.title(ticker + intval) 
        
        Total_buy_entries[ticker] = df["total_entry_b"][-1]
        Total_sell_entries[ticker] = df["total_entry_s"][-1]
        Strat_returns[ticker] = df["c_s_ret"][-1]*100
        BNH_returns[ticker] = df["bnh"][-1]*100
        
        #print("calculating KPIs for ",ticker) 
        ann_ret_str[ticker] =  ann_ret(df,d_p_day,"strategy_returns")
        ann_ret_bnh[ticker] =  ann_ret(df,d_p_day,"pct_change") 
        sharpe_strategy[ticker] = sharpe(df,0.05,d_p_day,"strategy_returns")
        sharpe_bnh[ticker] =  sharpe(df,0.05,d_p_day,"pct_change")
        drawdown_strategy[ticker] =  max_dd(df,"strategy_returns")
        drawdown_bnh[ticker] = max_dd(df,"pct_change") 

    KPI_df = pd.DataFrame([Total_buy_entries,Total_sell_entries,Strat_returns,BNH_returns,ann_ret_str,ann_ret_bnh,sharpe_strategy,sharpe_bnh,
                           drawdown_strategy,drawdown_bnh],index=["Total buy entries","Total sell entry","Strat_returns","BNH_returns","ann_ret_str","ann_ret_bnh",
                                                                  "sharpe_strategy","sharpe_bnh","drawdown_strategy","drawdown_bnh"])      
    
     
                                                                  
    return KPI_df.T 

#below loops can be used in order to cheak which combination is working right 
#for gamma in np.arange(0.05,0.26,0.02): 
    #for period in range(6,15,2):
         #for rsi_bul in range(10,31,2):
             #for rsi_ber in range(70,91,2):
#sma,emal,emas,lrsiup,lrsidown,sl%,tp%,commission%
#KPI(intval,datapoints,tickers_sector,data_capture_sector,gamma,parameters,duration)             
finserv15 = KPI("15minute",25,tickers_finserv,data_capture_finserv,0.21,   
                [200,50,20,[0.20,0.40],[0.60,0.80],3,8,10,90,0.01],"1-1-2021") 
print("period","str_mean",finserv15["Strat_returns"].mean()) 
            

auto60 = KPI("60minute",7,tickers_auto,data_capture_auto,0.21,   
               [200,50,20,[0.20,0.40],[0.60,0.80],3,9,20,80,0.01],"1-1-2021") 
print("strat_returns_mean",auto60["Strat_returns"].mean())  
print("BNH_returns_mean",auto60["BNH_returns"].mean()) 

auto_30 = KPI("30minute",13,tickers_auto,data_capture_auto,0.21,   
               [200,50,20,[0.20,0.40],[0.60,0.80],3,8,20,80,0.01],"1-1-2021") 
print("strat_returns_mean",auto_30["Strat_returns"].mean()) 
print("BNH_returns_mean",auto_30["BNH_returns"].mean())

auto_15 = KPI("15minute",25,tickers_auto,data_capture_auto,0.21,   
               [200,50,20,[0.20,0.40],[0.60,0.80],3,8,20,80,0.01],"1-1-2021") 
print("strat_returns",auto_15["Strat_returns"].mean())  
print("BNH_returns_mean",auto_15["BNH_returns"].mean()) 
 

#print("rsi period",period) 
#print("rsi bull",rsi_bull)
#print("rsi bear",rsi_bear) 


  
#change here to change lrsi
#df = d1["INFY"]
#df=lrsi(df,0.13)
#sma,emal,emas,lrsiup,lrsidown,sl%,tp%,commission%
#parameters=[200,50,20,[0.20,0.4],[0.6,0.80],3,6,0.01]
#df=backtest(df,parameters)

