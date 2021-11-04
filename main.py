import pandas as pd
from replit import db
import yfinance as yf
import numpy as np
from itertools import combinations
import math
from functions import *

class Result:
  def __init__(self, port: Port, entry):
    self.name = port.name
    self.entry = entry
    self.value = entry.iloc[0]['AnnualSharpeRatio']
  def __str__(self):
    return "Name: {name} \n{entry} \n AnnualSharpeRatio: {value}".format(name=self.name, entry=self.entry, value=self.value)
tickers = pd.read_json('./priceDataEligible.json')
tickersList = tickers.columns.tolist()

# allTickers = tickersList[:20]
allTickers = ['BTC-USD', 'DSI', 'TSLA', "VOO", "MSFT", "GME", "AAPL", "BABA"]
start_date = "2021-01-01"
end_date = "2021-10-20"
def getResult(tickerList):
  port = Port(tickerList)
  result = getStatsDF(port.data,port.weightDF)
  resultEntry = getMaxAnnualSharpeRatioEntry(result)
  newResultObj = Result(port, resultEntry)
  return newResultObj

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
  answer = (input('Do you wanna save? (N/y)') or 'n')
  if answer == 'n':
    return
  db[resultName] = resultDict[resultName].to_dict()


getBestPort(allTickers)

