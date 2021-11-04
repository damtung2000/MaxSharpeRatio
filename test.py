import pandas as pd
names = ['DJI', 'TSL']
dictDJI = {'DJI' : [1,2,3]}
dictTSL = {'TSL': [4,5,6]}
listDJI = [1,2,3]
listTSL = [4,5,6]
list
# dictOfDicts = {dictDJI, dictTSL}
listOfDicts = (dictDJI,dictTSL)
listOfLists = [listDJI, listTSL]

prepDataFrame = list(zip(list))
print(listOfDicts)
df = pd.DataFrame(prepDataFrame, columns=names)
print(df)