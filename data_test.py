# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:52:28 2020

@author: seang
"""
##Import Modules
import yfinance as yf
import pandas as pd
import datetime
import numpy as np

testTickers = ["VYM", "PGX", "AMZN", "DGRO", "HDV", "XLE", "AMD", "VMO", "BBF",
               "MSFT", "FHLC", "HYHG", "FNDE", "FNCMX", "FSDAX", "PGF", "TLT",
               "PFF", "SHYG", "FSCSX", "NOBL", "JPHY", "INTC"]

##Returns pd.dataframe of yfinance type, and ticker name
def getTickers(tckrs):
    tickerData = []
    for i in range(len(tckrs)):
        currentTicker = yf.Ticker(tckrs[i])
        tickerData.append(currentTicker)
    return tickerData


##Change pd.series to pd.df, make datetime from index to column 1
def indexToColumn(datedinfo):
    #assert(isinstance(datedinfo.index[1], datetime.date), "Wrong Data Type")
    #dateslist = datedinfo.index.copy()
    return None
    
#### CALCULATING METRICS ####
    

    
## Risk free rate of 1.1%, pulled from
#https://ycharts.com/indicators/10_year_treasury_rate#:~:text=10%20Year%20Treasury%20Rate%20is%20at%201.11%25%2C%20compared%20to%201.15,day%20and%201.81%25%20last%20year.
# Period is string type, can be [1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max]

# Return for Y stock in X period
#Price is int, 0 = Open, 1 = Close
    
def getPriceHistory(ticker, time):
    return ticker.history(period = time)
    
#Not real VWAP measure, but daily VWAP as we are testing using minimum month period
#Takes daily opening price, multiplies by volume, and finds that average
def getVWAP(tickerObj, price):
    total = tickerObj.iloc[:, price] * tickerObj["Volume"]
    volTotal = tickerObj["Volume"].sum()
    return total.sum()/volTotal


def getReturn(tickerObj, price, avg = True):
    stock = tickerObj
    if avg:
        initial = getVWAP(stock, price)
    else:   
        initial = stock.iloc[0, price]
    dividends = stock["Dividends"].sum()
    final = stock["Close"].mean() + dividends
    return (final - initial) / initial
    
    
# Standard Deviation for X period
    
def getStdDev(tickerObj, price):
    return tickerObj.iloc[:, price].std()
    

# Sharpe Ratio
# Assuming with decimals and not percentages, should yield same result- formula is (rp-rf)/stdDev
def getSharpeRatio(tickerObj, price, avg = True):
    rf = 0.011
    rp = getReturn(tickerObj, price, avg)
    stdDev = getStdDev(tickerObj, price)
    return ((rp - rf) / stdDev)*100

#this is average spread across specified time period
def getSpread(tickerObj):
    spread = tickerObj["High"] - tickerObj["Low"]
    return spread.mean()

def getAverageVolume(tickerObj):
    return tickerObj["Volume"].mean()

#Volume weighted spread, average spread per day weighted by volume traded per day
def getVWSpread(tickerObj):
    spread = tickerObj["High"] - tickerObj["Low"]
    spreadvol = spread.abs() * tickerObj["Volume"]
    totalvol = tickerObj["Volume"].sum()
    return spreadvol.sum()/totalvol

# VW Spread divided by VWAP as a measure of volatility
def getVolatility(tickerObj, price):
    spread = getVWSpread(tickerObj)
    price = getVWAP(tickerObj, price)
    return (spread/price)*100


# Dividend payout as a size relative to cost of investment
def getDividendSize(tickerObj, price):
    price = getVWAP(tickerObj, price)
    dividends = tickerObj["Dividends"]
    counter = 0
    avgsum = 0
    for i in range(len(dividends)):
        if dividends[i] != 0:
            avgsum += dividends[i]
            counter += 1
        else:
            continue
    if counter == 0:
        return 0
    else:
        avgdividend = (avgsum/counter)
        return (avgdividend/price)*100



#Builds feature matrix with the above metrics, with each column as a feature and each row a ticker
# Tickers is the original list of tickers as a list of strings
    
def buildFeatureMatrix(tickers, price, period, avg = True):
    features = 9
    counter = 0
    fmstarter = np.zeros((len(tickers), features))
    tickerObj = getTickers(tickers)
    for stock in tickerObj:
        currentFeatures = np.zeros(features)
        current = getPriceHistory(stock, period)
        currentFeatures[0] = getVWAP(current, price)
        currentFeatures[1] = (getReturn(current, price, avg))*100
        currentFeatures[2] = getStdDev(current, price)
        currentFeatures[3] = getSharpeRatio(current, price, avg)
        currentFeatures[4] = getVWSpread(current)
        currentFeatures[5] = getSpread(current)
        currentFeatures[6] = getAverageVolume(current)
        currentFeatures[7] = getVolatility(current, price)
        currentFeatures[8] = getDividendSize(current, price)
        fmstarter[counter, :] = currentFeatures
        counter += 1
    featureMatrix = pd.DataFrame(fmstarter, index = tickers, columns = ["VWAP", "Return", "StdDev", "Sharpe Ratio", 
                                "VWSpread", "Spread", "Average Volume", "Volatility", "Dividend Percentage"])
    return featureMatrix.dropna()

pd.options.display.max_columns = None
print(buildFeatureMatrix(testTickers, 1, "6mo", avg = False))
    

    
    
    
    
    
    
    