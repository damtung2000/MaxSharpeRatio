import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd
import json


# ticker_list = [
#     "DJI",
#     "TSLA",
# ]

def getData(ticker, start_date, end_date):
    # print(ticker)
    data = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
    dataname = ticker
    SaveData(data, dataname)

def SaveData(df, filename):
    df.to_csv("./" + filename + ".csv")

def getCloseData(ticker: str, startDate: str, endDate: str):
    data = yf.download(ticker, start=startDate, end=endDate)
    # print(data)
    adjCloseList = data["Adj Close"].tolist()
    # print(len(adjCloseList))
    return adjCloseList

def pullData(tickerList, name):
    start_date = "2021-01-01"
    end_date = "2021-10-20"
    dictOfDicts = {}
    for ticker in tickerList:
        closeData = getCloseData(ticker, startDate=start_date, endDate=end_date)
        dictOfDicts[ticker] = closeData
        # print('This is dictOfDict \n', dictOfDicts)
    # closeDataDF = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in dictOfDicts.items() ]))
    closeDataDF = pd.DataFrame({ key:pd.Series(value) for key, value in dictOfDicts.items() })
    closeDataDF.to_json(name)
    return

# # Get Tickers list
# readData = pd.read_csv("./tickersList.csv", usecols=["Name"])
# ticker_list = readData["Name"].tolist()

# Pull first data
# pullData(ticker_list, "./priceData.json")
# df= pd.read_json('./priceData.json')
# print(df.head(3))

# dfWithoutNan = df.dropna(axis=1)
# print(dfWithoutNan.head(5))
# dfWithoutNan.to_json('./priceDataEligible')

# finalDF = pd.read_json('./priceDataEligible')
# tsla = pd.read_csv('./TSLA.csv', usecols=["Date"])
# index = tsla["Date"].tolist()
# finalDF.index= index
# finalDF.to_excel('./priceData.xlsx')