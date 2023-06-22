"""
pm_school.py defines classes to fetch and analyse data from both sensor.community devices and APPA sensors.

L.Stipani, Trento, 2022
lorenzo(dot)stipani(at)gmail(dot)com
"""

import pandas as pd
import numpy  as np
import datetime
from matplotlib import pyplot as plt
from urllib.error import HTTPError


def smooth(y, win=5):
  """
  Smoothing by averaging data points (y) for given windowing extent (win)
  """
  return y.rolling(win).mean()


class sensor(object):
  """
  sensor object members
  -----
  date    : range of days as 'yyyy-mm-dd'
  sens_id : sensor id from sensor.community
  df      : pandas dataframe. Columns P1 = PM10, P2 = PM2.5
  
  filter() : return a pd.dataframe object with data filtered from date/hour ranges 
  plot()   : plot raw data and moving average for given windowing
  

  example calls
  -------------
  test = sensor('2022-05-20', '2022-05-27')
  newdf1 = test.filter(date=['2022-05-21','2022-05-21'], hour=[13,18])
  newdf2 = test.filter(date=['2022-05-21','2022-05-21'])
  test.plot(ma=10)
  """


  def __init__(self, start, end, sens_id=57925):
    """
    Args
    ----
    start   : 'yyyy-mm-dd'
    end     : 'yyyy-mm-dd'
    sens_id : sensor id from sensor.community
    """
    
    self.date    = [start, end]
    self.sens_id = sens_id
    self.df      = self._fetch()


  def _fetch(self):
    """
    Fetch sensor data from server
    """  
    dfs = []
    # loop over each day in [start, end]
    for dd in pd.period_range(self.date[0], self.date[1]): 
      try:
        df = pd.read_csv(self._make_url(dd), delimiter=';')
        dfs.append(df) # append to list of dataframes, one per day
      except HTTPError as err:
        if err.code == 404:
          print('csv not found for date: ' + str(dd))
  
    # make a total dataframe from each day
    tdf = pd.concat(dfs)
  
    # make a column with daily hours [0,23]
    tdf['dayhours'] = pd.DatetimeIndex(tdf['timestamp']).hour
    # clean up dataframe: cast timestamp into date format, set index as date
    tdf["datestamp"] = pd.to_datetime(tdf["timestamp"], format="%Y-%m-%d")
    tdf.set_index(["datestamp"], inplace=True)
    
    return tdf


  def _make_url(self, date):
    """
    URL string maker
    """
    if datetime.datetime.now().year != str(date)[:4]:
        up_folder = str(date)[:4] + '/'
    else:
        up_folder = '/'
    filename = str(date) + '_sds011_sensor_' + str(self.sens_id) + '.csv'
    url = 'https://archive.sensor.community/' + up_folder + str(date) + '/' + filename
    return url


  def _slice_date(self, df=None, start='', end=''):
    """
    Filter data by date range
    """
    if df is None:
      df = self.df

    if start == '' and end == '':
      return df
    elif start == '' :
      return df.loc[:end]
    elif end == '':
      return df.loc[start:]
    else:
      return df.loc[start:end]


  def _slice_hour(self, df=None, start=0, end=23):    
    """
    Filter data by hour range
    """
    if df is None:
      df = self.df

    return df.loc[(df['dayhours'] >= start) & (df['dayhours'] <= end)]

  
  
  def filter(self, date=['', ''], hour=[0, 23]):
    """
    Filter data from original data set. Return pd.dataframe.

    Args
    ----
    date : ['yyyy-mm-dd', 'yyyy-mm-dd']
    hour : [0, 23] 
    """
    
    df = self._slice_date(start=date[0], end=date[1])
    return self._slice_hour(df = df, start=hour[0], end=hour[1])


  def plot(self, date=['', ''], hour=[0, 23], ma=0):
    """
    Plot data.
    
    Args
    ----
      ma : rolling window for moving average
    """
    
    pdf = self.filter(date=date, hour=hour)

    # do stats and plot
    if ma == 0:
      pdf[["P1","P2"]].plot(figsize=(10,10), linestyle='-', marker='o')
      plt.legend(["PM 10", "PM 2.5"]) ### mind that column P1 = PM10, P2 = PM2.5 !!
    else:
      pdf["P1_MA"] = smooth(pdf["P1"], ma)
      pdf["P2_MA"] = smooth(pdf["P2"], ma)
      pdf[["P1_MA","P2_MA"]].plot(figsize=(10,10))
      plt.legend(["PM 10 - MA ({:d})".format(ma), "PM 2.5 - MA ({:d})".format(ma)])

    # cosmetics
    plt.xlabel('Tempo')
    plt.ylabel(r'Valore / $\mu g/m^3$')
    plt.title('Sensor PM')
    plt.show()





class appa(object):
  """
  appa object members
  -----
  date   : either 'last' (=last day avail), 'yyyy-mm-dd' (=specify day) or 'yyyy-mm-dd,yyyy-mm-dd' (=range of days)
  sensor : list of any elements among {'trento.s.chiara', 'trento.v.bolzano', 'rovereto', 'b.valsug', 'r.garda', 'm.gaza', 'p.rotal', 'avio'}
  df     : pandas dataframe
  
  plot() : plot raw data as time series
  

  example calls
  -------------
  ap = appa(date = '2022-05-20', sensor = ['trento.s.chiara', 'rovereto'])
  ap.plot()
  """

  def __init__(self, **kwargs):
    self.df = self._get(**kwargs)

  def plot(self):
    for k in list(self.df["Inquinante"].unique()):
      dd = self.df.loc[self.df["Inquinante"] == k]
      plt.plot(dd["Ora"], dd["Valore"], "*-", label=str(k))

    plt.legend()
    plt.xlabel("Ora del giorno")
    plt.ylabel("Valore / "+str(self.df["Unità di misura"].unique()))

    plt.title("Misurazioni APPA in data "+self.date)
    plt.show()

  def _get(self, date='last', sensor=['trento.s.chiara']):
    """
    Args
      date:    one among 'last', 'yyyy-mm-dd', 'yyyy-mm-dd,yyyy-mm-dd'
      sensor:  sequence among 'trento.s.chiara', 'trento.v.bolzano', 'rovereto', 'b.valsug', 'r.garda', 'm.gaza', 'p.rotal', 'avio'
    """
    cod = {'trento.s.chiara': 2,
          'trento.v.bolzano': 4,
          'rovereto': 6,
          'b.valsug': 8,
          'r.garda': 9,
          'm.gaza': 15,
          'p.rotal': 22,
          'avio': 23}

    url = 'https://bollettino.appa.tn.it/aria/opendata/csv/' + date
    ids = "/"
    for k in sensor:
      ids = ids + str(cod[k]) + ','
    url = url + ids[0:-1]
    
    self.date = date
    return pd.read_csv(url, encoding="ISO-8859-1")

