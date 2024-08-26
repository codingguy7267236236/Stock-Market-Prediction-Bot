import yfinance as yf
from pandas_datareader import data as pdr
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
import xgboost as xgb
import pandas as pd

yf.pdr_override()

class StockModel():
  def __init__(self, ticker):
    self.ticker = ticker
    self.SetDates()

  def SetDates(self,start=None,end=None):
    self.start = start
    self.end = end
    if end == None:
      self.end = dt.now()

    if start == None:
      self.start = dt(self.end.year,self.end.month,self.end.day,9,0,0)

  def GetData(self,period):
    self.data = pdr.get_data_yahoo(self.ticker.upper(), start=self.start, end=self.end, interval=period)
    self.period = period
    return self.data

  def Forecast(self):
    dta = self.GetData(self.period)
    mdt = dta.iloc[-1]
    mdt = [mdt["Open"],mdt['Volume'],mdt['High'],mdt['Low']]
    fore = self.Predict([mdt])
    return fore[0]


  def Train(self):
    self.train_data = self.data.iloc[:int(.80*len(self.data)), :]
    #train_data = dta
    self.test_data = self.data.iloc[int(.80*len(self.data)):, :]

    #define the features and target variable
    #input data things
    self.features = ['Open','Volume','High','Low']
    #target is what our output for model will be
    self.target = "Adj Close"

    #create and train model
    self.model = xgb.XGBRegressor()
    self.model.fit(self.train_data[self.features], self.train_data[self.target])

  def Predict(self,data):
    predict = self.model.predict(data)
    return predict

  def Score(self,train=True):
    if train==True:
      self.Train()
    self.acc = self.model.score(self.test_data[self.features],self.test_data[self.target])
    #print(f"Model {self.period} Accuracy {self.acc}")
    return self.acc

  def Chart(self,label='Open'):
    self.Train()
    #predict
    lab = label
    predictions = self.Predict(self.test_data[self.features])
    #print("Predictions: ")
    #print(predictions)
    #print("\nActual: ")
    #print(test_data[lab])

    #scores
    self.Score(False)

    times = []
    strt = 0
    for i in predictions:
      times.append(strt*15)
      strt += 15

    fig = plt.figure()
    plt.plot(times,predictions,label="Prediction",c="y")
    plt.plot(times,self.test_data[lab],label="Actual",c="b")
    fig.suptitle(f"Model for {self.period} ({self.acc*100}%)")
    plt.xlabel(f"Num of {self.period}")
    plt.legend()
    plt.savefig(f"model_{self.period}.png")
    plt.cla()
    plt.clf()
    plt.close()

  def Plot(self,x,y):
    fig = plt.figure()
    plt.plot(x,y,label="Prediction",c="y")
    fig.suptitle(f"{self.ticker} Prediction over next day")
    plt.legend()
    fp = f"model_predictions.png"
    plt.savefig(fp)
    plt.cla()
    plt.clf()
    plt.close()
    return fp


def GetStock(ticker,period,backlog):
  nvda = StockModel(ticker)

  now = dt.now()
  start = now - timedelta(backlog)
  nvda.SetDates(start,now)
  dta = nvda.GetData(period)
  return nvda