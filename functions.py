import pandas as pd
from replit import db
import yfinance as yf
import numpy as np
from itertools import combinations
import math

tickerList = ['BTC-USD', 'DSI', 'TSLA']
start_date = "2021-01-01"
end_date = "2021-10-20"











def getCloseData(ticker: str, startDate: str, endDate: str):
    data = yf.download(ticker, start=startDate, end=endDate)
    # print(data)
    # data.set_index('Date')
    index = data.index.strftime('%Y-%m-%d')
    data.index = index
    adjCloseDF = data["Adj Close"]
    # print(adjCloseDF)
    return adjCloseDF

def pullDataToDatabase(tickerList,start_date = "2021-01-01",end_date = "2021-10-20"):
    for ticker in tickerList:
        closeData = getCloseData(ticker, startDate=start_date, endDate=end_date)
        print(type(closeData))
        db[ticker] = closeData.T.to_dict()
## TODO: remove nan data
def getRawPriceFromDB(key: str):
  data = db[key]
  df = pd.DataFrame.from_dict(data, orient='index',columns=['Price'])
  df.index.name ='Date'
  df.reset_index(inplace=True)
  return df


# tsla = getRawPriceFromDB('TSLA')
# dsi = getRawPriceFromDB('DSI')
# btc = getRawPriceFromDB('BTC-USD')

def getReturnDaily(portData: dict):
  newData = {}
  for name in portData.keys():
    df = portData[name]
    priceArray = df['Price']
    returnArray = [np.nan]
    for i in range(1, len(priceArray[1:])+ 1):
      realizedReturn = (priceArray[i] - priceArray[i-1])/priceArray[i-1]
      returnArray.append(realizedReturn)
    # print(returnArray, '\n', len(returnArray))
    df['Return'] = returnArray
    newData[name] = df
  return newData

def tryToGetData(nameArray):
  keys = db.keys()
  notPulledYet = list(filter(lambda ticker: ticker not in keys,nameArray))
  if notPulledYet:
    print('Not pulled yet: {}, pulling...'.format(notPulledYet))
    pullDataToDatabase(notPulledYet)
  data = {}
  for ticker in nameArray:
    data[ticker] = getRawPriceFromDB(ticker)
  return data

class Port:
  def __init__(self,nameArray):
    self.name = nameArray
    self.data = getReturnDaily(mergeDates(tryToGetData(nameArray), nameArray))
    self.weightDF = createRandomWeightDF(nameArray)
  def __str__(self):
    return "{name}:\n {data}".format(name=self.name, data=self.data.values())



def getStdev(df):
  return df['Return'].std(ddof=0)

def getExReturn(df):
  return df['Return'].mean()


def getCov(df1, df2):
  return df1['Return'].cov(df2['Return'])

def getCorrel(df1,df2):
  return df1['Return'].corr(df2['Return'])

def getReturnPort(port, weightArray):
  portArray = list(port.values())
  exReturnPort = 0
  for i in range(3):
    exReturnPort += getExReturn(portArray[i])*weightArray[i]
  return exReturnPort

def createRandomWeightDF(nameArray):
  weights1 = np.random.default_rng().uniform(0,0.5,300).round(2)
  weights2 = np.random.default_rng().uniform(0,0.5,300).round(2)
  weights3 = []
  for i in range(300):
    weights3.append(1-weights1[i]-weights2[i])
  return pd.DataFrame({nameArray[0]: weights1, nameArray[1]: weights2, nameArray[2]: weights3})

def mergeDates(port, nameArray):
  df1 = port[nameArray[0]]
  df2 = port[nameArray[1]]
  df3 = port[nameArray[2]]
  merged = df1.merge(df2,on='Date').merge(df3,on='Date')
  merged.columns = ['Date', *nameArray]
  newObj = {}
  for ticker in nameArray:
    newDF = merged.filter(['Date',ticker], axis=1)
    newDF.columns = ['Date', 'Price']
    newObj[ticker] = newDF
  return newObj

port = Port(tickerList)
print(port)
# for ticker in tickerList:
#   print(newObj[ticker])

def calPart1(weight,sigma):
  return weight**2*sigma**2

def calPart2(weight1,weight2,cov):
  return 2*weight1*weight2*cov

def getStdevPort(port: dict, weightArray):
  portArray = list(port.values())
  variance = 0
  for i in range(3):
    # Cal part 1
    weight = weightArray[i]
    sigma = getStdev(portArray[i])
    variance += calPart1(weight, sigma)
  
  combination = [*combinations(range(3), 2)]
  for pair in combination:
    # Cal part 2
    weight1 = weightArray[pair[0]]
    weight2 = weightArray[pair[1]]
    cov = getCov(portArray[pair[0]], portArray[pair[1]])
    variance += calPart2(weight1, weight2, cov)
  
  return math.sqrt(variance)

def getDailySharpeRatio(port, weightArray, riskFreeRate=0.00025):
  returnPort = getReturnPort(port,weightArray)
  stdevPort = getStdevPort(port,weightArray)
  return (returnPort - riskFreeRate)/stdevPort

def getAnnualizedSharpeRatio(port, weightArray, riskFreeRate=0.00025):
  dailySharpeRatio = getDailySharpeRatio(port, weightArray, riskFreeRate)
  return dailySharpeRatio * math.sqrt(252)

def getStatsPort(port, weightArray, riskFreeRate=0.00025):
  returnPort = getReturnPort(port,weightArray)
  stdevPort = getStdevPort(port,weightArray)
  dailySharpeRatio = (returnPort - riskFreeRate)/stdevPort
  annualizedSharpeRatio = dailySharpeRatio * math.sqrt(252)
  
  return (returnPort, stdevPort, dailySharpeRatio, annualizedSharpeRatio)

def getStatsDF(port, weightDF):
  returnPortArray = []
  stdevPortArray = []
  dailySharpeRatioArray = [] 
  annualizedSharpeRatioArray = []
  for index, row in weightDF.iterrows():
    weightArray = row.tolist()
    returnPort, stdevPort, dailySharpeRatio, annualizedSharpeRatio = getStatsPort(port,  weightArray)
    returnPortArray.append(returnPort)
    stdevPortArray.append(stdevPort)
    dailySharpeRatioArray.append(dailySharpeRatio)
    annualizedSharpeRatioArray.append(annualizedSharpeRatio)
  result = weightDF.copy()
  result['ReturnPort'] = returnPortArray
  result['StdevPort'] = stdevPortArray
  result['DailySharpeRatio'] = dailySharpeRatioArray
  result['AnnualSharpeRatio'] = annualizedSharpeRatioArray
  return result

def saveDataToDatabase(df, nameArray):
  dbName = ', '.join(nameArray)
  if dbName in db.keys():
    answer = (input('Record already exist for {}. \nOverwrite? (N/y)'.format(dbName)) or 'n')
    if (answer == 'n'):
      print('Did not overwrite {}, cancelling...'.format(dbName))
      return
  
  db[dbName] = df.to_dict()

def getResultFromDatabase(key):
  dfDict = db[key]
  return pd.DataFrame.from_dict(dfDict, orient='index').T


def getMaxAnnualSharpeRatioEntry(resultDF):
  return resultDF[resultDF['AnnualSharpeRatio']==resultDF['AnnualSharpeRatio'].max()]

# obj = {'df1': btc, 'df2': dsi, 'df3': tsla}


# newObj = mergeDates(**obj)
# # print(newObj)

# getReturnDaily(newObj[tickerList[0]])
# getReturnDaily(newObj[tickerList[1]])
# getReturnDaily(newObj[tickerList[2]])

# weightDF = createRandomWeightDF(tickerList)

# result = getStatsDF(newObj, weightDF)
# print(result)
# saveDataToDatabase(result,tickerList)
# newDF = getResultFromDatabase(', '.join(tickerList))
# print('This is newDF\n', newDF)
# print(getMaxAnnualSharpeRatioEntry(newDF))

# print(getStdevPort(newObj,[0.1,0.5,0.4]))
# print(getReturnPort(newObj,[0.1,0.5,0.4]))

