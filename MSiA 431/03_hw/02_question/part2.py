from pyspark import SparkContext, SparkConf
from datetime import datetime
import numpy as np
from itertools import combinations

conf = SparkConf().setAppName("Chicago Crime Data Analysis")
sc = SparkContext(conf=conf)

# Load the data from HDFS
crimeData = sc.textFile("hdfs://wolf:9000/user/sms5736/03_hw/Crimes_-_2001_to_present.csv")

# Extract header
header = crimeData.first()
crimeData = crimeData.filter(lambda line: line != header)

# Take a small sample of the data
# crimeData = crimeData.sample(False, 0.001)  # 1% of the data

def parse(line):
    fields = line.split(',')
    date = datetime.strptime(fields[2], '%m/%d/%Y %I:%M:%S %p')
    beat = fields[10]  # adjust field index according to your data
    return (date, beat)

# Parse the RDD
crimeDataParsed = crimeData.map(parse)

# Filter for the last 5 years
crimeDataLast5Years = crimeDataParsed.filter(lambda x: x[0].year >= datetime.now().year - 5)

# Count the number of crimes per beat per year
beatCountsPerYear = crimeDataLast5Years.map(lambda x: ((x[1], x[0].year), 1)).reduceByKey(lambda a, b: a + b)

# Get all beats
beats = beatCountsPerYear.map(lambda x: x[0][0]).distinct().collect()

# Sort the counts by year for each beat and persist it
beatCountsPerYearSorted = beatCountsPerYear.map(lambda x: (x[0][0], (x[0][1], x[1]))).groupByKey().mapValues(sorted).persist()

# Calculate the correlation for each pair of beats
correlations = []
for beat1, beat2 in combinations(beats, 2):
    beat1Counts = beatCountsPerYearSorted.lookup(beat1)[0]
    beat2Counts = beatCountsPerYearSorted.lookup(beat2)[0]

    if len(beat1Counts) != len(beat2Counts):  # if there are missing years for a beat, skip this pair
        continue

    beat1CountsValues = [x[1] for x in beat1Counts]
    beat2CountsValues = [x[1] for x in beat2Counts]

    correlation = np.corrcoef(beat1CountsValues, beat2CountsValues)[0, 1]
    correlations.append(((beat1, beat2), correlation))

# Top x
num_top = 1000

# Sort by correlation and print the pairs with the highest correlations
correlations.sort(key=lambda x: x[1], reverse=True)

# Open a file to write the result
with open('top_1000_higest_correlated_beats.txt', 'w') as f:
    for pair, correlation in correlations[:num_top]:
        f.write(f'Beats: {pair}, Correlation: {correlation}\n')
