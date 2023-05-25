from pyspark.sql.functions import to_timestamp

# Assuming 'Date' is your timestamp column
df = df.withColumn('Date', to_timestamp('Date', 'MM/dd/yyyy hh:mm:ss a'))

from pyspark.sql.functions import hour, dayofweek, month

df = df.withColumn('Hour', hour(df['Date']))
df = df.withColumn('DayOfWeek', dayofweek(df['Date']))
df = df.withColumn('Month', month(df['Date']))

df_arrests = df.filter(df['Arrest'] == True)

df_hourly = df_arrests.groupBy('Hour').count().orderBy('Hour')
df_weekly = df_arrests.groupBy('DayOfWeek').count().orderBy('DayOfWeek')
df_monthly = df_arrests.groupBy('Month').count().orderBy('Month')

df_hourly.show()
df_weekly.show()
df_monthly.show()
