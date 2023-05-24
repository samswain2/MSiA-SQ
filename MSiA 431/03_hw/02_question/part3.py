from pyspark import SparkContext, SparkConf
from datetime import datetime
from math import sqrt

conf = SparkConf().setAppName("Chicago Crime Data Analysis")
sc = SparkContext(conf=conf)

sc.setLogLevel("ERROR")

# Load the data from HDFS
crimeData = sc.textFile("hdfs://wolf:9000/user/sms5736/03_hw/Crimes_-_2001_to_present.csv")

# Extract header
header = crimeData.first()
crimeData = crimeData.filter(lambda line: line != header)

def parse(line):
    fields = line.split(',')
    date = datetime.strptime(fields[2], '%m/%d/%Y %I:%M:%S %p')
    block = fields[3]  # adjust field index according to your data
    return (date, block)

# Parse the RDD
crimeDataParsed = crimeData.map(lambda line: (line.split(',')[3], 1))

# Filter for the time during which each mayor was in office
dalyCrimes = crimeDataParsed.filter(lambda x: datetime(1989, 4, 24) <= x[1] <= datetime(2011, 5, 16))
emanuelCrimes = crimeDataParsed.filter(lambda x: datetime(2011, 5, 16) < x[1] <= datetime(2019, 5, 20))

# Calculate sum and count for each block during each mayor's term
def seqOp(x, y):
    return (x[0] + y, x[1] + y, x[2] + y*y)

def combOp(x, y):
    return (x[0] + y[0], x[1] + y[1], x[2] + y[2])

zeroValue = (0, 0.0, 0.0)

dalyBlockStats = dalyCrimes.aggregateByKey(zeroValue, seqOp, combOp)
emanuelBlockStats = emanuelCrimes.aggregateByKey(zeroValue, seqOp, combOp)

# Calculate mean and standard deviation for each block during each mayor's term
def calcStats(sum_count_sqcount):
    count, sum, sqcount = sum_count_sqcount
    mean = sum / count
    std_dev = sqrt(sqcount / count - mean*mean)
    return (mean, std_dev, count)

dalyBlockStats = dalyBlockStats.mapValues(calcStats)
emanuelBlockStats = emanuelBlockStats.mapValues(calcStats)

# Save the statistics for each block during each mayor's term
with open('daly_block_stats.txt', 'w') as f:
    for key, value in dalyBlockStats.collect():
        f.write(str(key) + ': ' + str(value) + '\n')

with open('emanuel_block_stats.txt', 'w') as f:
    for key, value in emanuelBlockStats.collect():
        f.write(str(key) + ': ' + str(value) + '\n')
