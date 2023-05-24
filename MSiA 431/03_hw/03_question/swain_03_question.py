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

# load the other file
other_df = spark.read.format("csv").option("header", "true").load("hdfs:///user/sms5736/03_hw/IUCR.csv")

# rename the 'IUCR' column in the other dataframe before joining
other_df = other_df.withColumnRenamed("IUCR", "IUCR_other")

# join the two dataframes on the renamed column
joined_df = df.join(other_df, df.IUCR == other_df.IUCR_other, 'inner')

# Create a temporary view of the dataframe
joined_df.createOrReplaceTempView("crime_data")

# Query data using sparksql
result = spark.sql("""

    SELECT `PRIMARY DESCRIPTION` as Desc
    FROM crime_data

""")

result.show()