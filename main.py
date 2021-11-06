import pandas as pd
from replit import db
import yfinance as yf
import numpy as np
from itertools import combinations
import math
from functions import *

def getWeightArray(entry):
  weightArray = entry.iloc[0:3].values.tolist()
  print(weightArray)
  return weightArray

def getRealizedStats(tickerList, weightArray):
  port = Port(tickerList)
  # print(port.realizedData)
  realizedAnnualSharpe = getAnnualizedSharpeRatio(port.realizedData,weightArray)
  return realizedAnnualSharpe

class Result:
  def __init__(self, port: Port, entry):
    self.name = port.name
    self.entry = entry
    self.weightArray = getWeightArray(entry)
    self.value = entry['AnnualSharpeRatio']
  def __str__(self):
    return "Name: {name} \n{entry} \n AnnualSharpeRatio: {value}".format(name=self.name, entry=self.entry, value=self.value)
# tickers = pd.read_json('./priceDataEligible.json')
# tickersList = tickers.columns.tolist()

# allTickers = tickersList[:20]
allTickers = ['BTC-USD', 'DSI', 'TSLA', "VOO", "MSFT", "GME", "AAPL", "BABA"]
# start_date = "2021-01-01"
# end_date = "2021-10-20"
def getResult(tickerList, weightArray=None):
  if not weightArray:
    port = Port(tickerList)
    resultEntry = getStatsDF(port.pastData,port.weightDF)
    newResultObj = Result(port, resultEntry)
    return newResultObj
  else:
    # pullDataToDatabase(tickerList, '2021-08-01', '2021-10-20')
    port = Port(tickerList)
    realizedAnnualSharpe = getAnnualizedSharpeRatio(port.realizedData,weightArray)
    return realizedAnnualSharpe
# print(getResult(tickerList))

def getBestPort(allTickers):
  tickerCombinations = combinations(allTickers,3)
  resultDict = {}
  for tickerList in tickerCombinations:
    result = getResult(tickerList)
    resultDict[result.name] = result
  bestValue = 0
  resultName = ''
  #Get Best
  for result in resultDict.values():
    if result.value > bestValue:
      bestValue = result.value
      resultName = result.name
  print('Best Sharpe: {value}\n{entry}'.format(value=bestValue, entry=resultDict[resultName]))
  
  pastResultRef = resultDict[resultName]
  realizedAnnualSharpe = getRealizedStats(pastResultRef.name,pastResultRef.weightArray)
  print(realizedAnnualSharpe)
  
  # # Pull new data
  # pullDataToDatabase(pastResultRef.name,"2021-08-01","2021-10-20")

  # newPort = Port(pastResultRef.name)

  # getAnnualizedSharpeRatio(newPort.data,pastResultRef.weightArray)

  # answer = (input('Do you wanna save? (N/y)') or 'n')
  # if not(answer == 'n'):
  #   db[resultName] = resultDict[resultName].entry.to_dict()
  #   print('Saved Entry as key {}'.format(resultName))
  
# for key in db.keys():
#   del db[key]


 
    






# getBestPort(allTickers)

# port = Port(["BTC-USD", "MSFT", "GME"])
port = ["BTC-USD", "MSFT", "GME"]
result = getBestPort(port)
print('Done')
# for name in port.pastData.keys():
#   port.pastData[name].to_csv('./{}.csv'.format(name))
  

