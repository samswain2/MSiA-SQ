from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.functions import to_timestamp, hour, dayofweek, month
import matplotlib.pyplot as plt
import pandas as pd

conf = SparkConf().setAppName("Chicago Crime Data Analysis")
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
sqlContext = SQLContext(sc)

# Load the data from HDFS
crimeData = sqlContext.read.format("csv").option("header","true").load("hdfs://wolf:9000/user/sms5736/03_hw/Crimes_-_2001_to_present.csv")

# Assuming 'Date' is your timestamp column
crimeData = crimeData.withColumn('Date', to_timestamp('Date', 'MM/dd/yyyy hh:mm:ss a'))

crimeData = crimeData.withColumn('Hour', hour(crimeData['Date']))
crimeData = crimeData.withColumn('DayOfWeek', dayofweek(crimeData['Date']))
crimeData = crimeData.withColumn('Month', month(crimeData['Date']))

df_arrests = crimeData.filter(crimeData['Arrest'] == 'true')

df_hourly = df_arrests.groupBy('Hour').count().orderBy('Hour')
df_weekly = df_arrests.groupBy('DayOfWeek').count().orderBy('DayOfWeek')
df_monthly = df_arrests.groupBy('Month').count().orderBy('Month')

# Convert the Spark DataFrames to pandas DataFrames
df_hourly_pd = df_hourly.toPandas()
df_weekly_pd = df_weekly.toPandas()
df_monthly_pd = df_monthly.toPandas()

# Plot the data and save the plots
df_hourly_pd.plot(kind='bar', x='Hour', y='count', title='Hourly Arrests')
plt.savefig('hourly_arrests.png')
df_weekly_pd.plot(kind='bar', x='DayOfWeek', y='count', title='Weekly Arrests')
plt.savefig('weekly_arrests.png')
df_monthly_pd.plot(kind='bar', x='Month', y='count', title='Monthly Arrests')
plt.savefig('monthly_arrests.png')

# Save the pandas DataFrames to text files
df_hourly_pd.to_csv('hourly_arrests.txt', index=False)
df_weekly_pd.to_csv('weekly_arrests.txt', index=False)
df_monthly_pd.to_csv('monthly_arrests.txt', index=False)
