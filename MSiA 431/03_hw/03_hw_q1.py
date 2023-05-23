from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Chicago Crime Analysis").getOrCreate()

# Load the data
df = spark.read.format("csv").option("header", "true").load("/home/public/crime")

from pyspark.sql.functions import to_date, col

# Convert 'Date' column to datetime type
df = df.withColumn("Date", to_date(col("Date"), 'MM/dd/yyyy hh:mm:ss a'))

# Create a temporary view of the dataframe
df.createOrReplaceTempView("crime_data")

# Query to generate the histogram
result = spark.sql("""
    SELECT MONTH(Date) AS Month, COUNT(*) AS Crime_Events
    FROM crime_data
    GROUP BY MONTH(Date)
    ORDER BY MONTH(Date)
""")

# Show the results
result.show()
