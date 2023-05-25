from pyspark import SparkContext, SparkConf
from datetime import datetime

conf = SparkConf().setAppName("Chicago Crime Data Analysis")
sc = SparkContext(conf=conf)

# Load the data from HDFS
crimeData = sc.textFile("hdfs://wolf:9000/user/sms5736/03_hw/Crimes_-_2001_to_present.csv")

# Extract header
header = crimeData.first()
crimeData = crimeData.filter(lambda line: line != header)

# Assuming the date field is in the format 'MM/dd/yyyy' and at the 2nd index position
def parse(line):
    fields = line.split(',')
    date = datetime.strptime(fields[2], '%m/%d/%Y %I:%M:%S %p')
    block = fields[3]  # adjust field index according to your data
    return (date, block)

# Parse the RDD
crimeDataParsed = crimeData.map(parse)

# Find the last date in the dataset
lastDateInDataset = crimeDataParsed.map(lambda x: x[0]).max()

# Filter for the last 3 years
crimeDataLast3Years = crimeDataParsed.filter(lambda x: x[0].year >= lastDateInDataset.year - 3)

# Count the number of crimes per block
blockCounts = crimeDataLast3Years.map(lambda x: (x[1], 1)).reduceByKey(lambda a, b: a + b)

# Get the top 10 blocks
top10Blocks = blockCounts.takeOrdered(10, key=lambda x: -x[1])

# Open a file to write the result
with open('top_10_crime_blocks_last_3_years.txt', 'w') as f:
    for row in top10Blocks:
        f.write(f"Block: {row[0]}, Number of Crimes: {row[1]}\n")
