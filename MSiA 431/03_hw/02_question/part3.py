from pyspark import SparkContext, SparkConf
from datetime import datetime

conf = SparkConf().setAppName("Chicago Crime Data Analysis")
sc = SparkContext(conf=conf)

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
crimeDataParsed = crimeData.map(parse)

# Filter for the time during which each mayor was in office
# NOTE: Replace with the actual dates of each mayor's term
dalyCrimes = crimeDataParsed.filter(lambda x: datetime(1989, 4, 24) <= x[0] <= datetime(2011, 5, 16))
emanuelCrimes = crimeDataParsed.filter(lambda x: datetime(2011, 5, 16) < x[0] <= datetime(2019, 5, 20))

# Count the number of crimes during each mayor's term
dalyCount = dalyCrimes.count()
emanuelCount = emanuelCrimes.count()

# Open a file to write the result
with open('mayor_crime_nums.txt', 'w') as f:
    f.write(f'Number of crime events during Mayor Daly\'s term: {dalyCount}\n')
    f.write(f'Number of crime events during Mayor Emanuel\'s term: {emanuelCount}')
