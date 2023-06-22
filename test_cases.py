"""
Examples with data from sensor.community
"""

import pm_school
import matplotlib.pyplot as plt


#------------------------------------------------------------
### 0) fetch data in given date range

df = pm_school.sensor(start='2022-06-10', end='2022-06-24')



#--------------------------------------------------------------------------------------------
### 1) filter data by day and hour ranges, then plot only PM10 (i.e. P1 column of dataframe)

df.filter(['2022-06-18','2022-06-20'], hour=[6,10])["P1"].plot()
plt.show()



#-------------------------------------------------------------
### 2) plot data filtered by date range, w/ and w/o smoothing

df.plot(date=['2022-06-18','2022-06-18'], ma=0)
df.plot(date=['2022-06-18','2022-06-18'], ma=20)



#-------------------------------------------------------------
### 3) histograms of data at different hour intervals

mydf = df.filter(hour=[6,9])
plt.hist(mydf["P2"], bins=20, alpha=0.5, label="6..9")
mydf = df.filter(hour=[10,15])
plt.hist(mydf["P2"], bins=20, alpha=0.5, label="10..15")
mydf = df.filter(hour=[16,21])
plt.hist(mydf["P2"], bins=20, alpha=0.5, label="16..21")
plt.legend()
plt.show()



#------------------------------------------------------------------------
### 4) time correlations between PM2.5 and PM10 in a given range of days

mydf = df.filter(date=['','2022-06-18']) # dates: from first of dataset to 2022-06-18
y1 = pm_school.smooth(mydf["P1"], 10) # smoothing of filtered data
y2 = pm_school.smooth(mydf["P2"], 10)

f, axs = plt.subplots(1,2,figsize=(12,5))
axs[0].plot(y1.tolist(), label="PM10 : ma(10)") # y1 is a pandas Series object, here is cast to list by tolist() for feeding the plt.plot routine
axs[0].plot(y2.tolist(), label="PM2.5 : ma(10)")
axs[0].set_xlabel('time unit')
axs[0].set_ylabel(r'Density $\mu g/m^3$')
axs[0].set_title("Moving Average of PM data in [2022-06-15, 2022-06-18]")
axs[0].legend()

axs[1].plot(y1.tolist(),y2.tolist(),'*')
axs[1].set_xlabel(r"PM 10 $\mu g/m^3$")
axs[1].set_ylabel(r"PM 2.5 $\mu g/m^3$")
axs[1].set_title("linear correlation R = {:.3f}".format(y1.corr(y2))) # .corr() is a pandas definied method for evaluating the Pearson's Correlation
plt.show()
