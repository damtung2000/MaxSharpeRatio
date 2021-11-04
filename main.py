import pandas as pd
from replit import db
import yfinance as yf
import numpy as np
from itertools import combinations
import math
from functions import *

tickerList = ['BTC-USD', 'DSI', 'TSLA']
start_date = "2021-01-01"
end_date = "2021-10-20"

port = Port(tickerList)
print(port)

result = getStatsDF(port.data,port.weightDF)

resultEntry = getMaxAnnualSharpeRatioEntry(result)
print(resultEntry)


