# Import necessary libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, col
import matplotlib.pyplot as plt

# Initialize a SparkSession
spark = SparkSession.builder.appName("Chicago Crime Analysis").getOrCreate()

# Set log level to reduce console output
spark.sparkContext.setLogLevel("ERROR")

# Load the data from HDFS
df = spark.read.format("csv").option("header", "true").load("hdfs:///user/sms5736/03_hw/Crimes_-_2001_to_present.csv")

# Convert 'Date' column to datetime type
df = df.withColumn("Date", to_date(col("Date"), 'MM/dd/yyyy hh:mm:ss a'))

# Create a temporary view of the dataframe
df.createOrReplaceTempView("crime_data")

# SQL Query to generate the average number of crimes per month over the years
result = spark.sql("""
    SELECT Month, ROUND(AVG(Crime_Count), 2) as Average_Crime_Events
    FROM (
        SELECT YEAR(Date) as Year, MONTH(Date) as Month, COUNT(*) as Crime_Count
        FROM crime_data
        GROUP BY YEAR(Date), MONTH(Date)
    ) as inner_table
    GROUP BY Month
    ORDER BY Month
""")

# Collect the result as a list of Row
result_collect = result.collect()

# Open a file to write the result
with open('swain_01_output.txt', 'w') as f:
    for row in result_collect:
        f.write(f"Month: {row['Month']}, Average_Crime_Events: {row['Average_Crime_Events']}\n")

# Convert the Spark DataFrame to Pandas for plotting
result_pd = result.toPandas()

# Create a bar plot of the average crime events by month
plt.bar(result_pd['Month'], result_pd['Average_Crime_Events'])
plt.xlabel('Month')
plt.ylabel('Average Number of Crime Events')
plt.title('Histogram of average crime events by month')
plt.savefig('swain_01_hist.png')
