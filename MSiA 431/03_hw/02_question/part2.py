from pyspark import SparkContext, SparkConf
from datetime import datetime
from pyspark.mllib.stat import Statistics
from pyspark.mllib.linalg import Vectors

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
    beat = fields[10]  # adjust field index according to your data
    return (date, beat) if beat.isdigit() and len(beat) == 4 else None

# Parse the RDD
crimeDataParsed = crimeData.map(parse).filter(lambda x: x is not None)

# Filter for the last 5 years
most_recent_date = datetime(2019, 12, 31)  # set the most recent date
crimeDataLast5Years = crimeDataParsed.filter(lambda x: x[0].year >= most_recent_date.year - 5)

# Create a set of all unique beats
all_beats = crimeDataLast5Years.map(lambda x: x[1]).distinct().filter(lambda beat: beat.isdigit() and len(beat) == 4).collect()
all_beats_dict = {beat: index for index, beat in enumerate(all_beats)}
num_beats = len(all_beats)

# Count the number of crimes per beat per year and switch the order of beat and year
beatCountsPerYear = crimeDataLast5Years.map(lambda x: ((x[0].year, x[1]), 1)).reduceByKey(lambda a, b: a + b)

# Create a full vector for each year
beatCountsPerYearFull = beatCountsPerYear.map(lambda x: (x[0][0], (all_beats_dict[x[0][1]], x[1]))).groupByKey()

def fill_vector(counts):
    vec = [0] * num_beats
    for beat_index, count in counts:
        vec[beat_index] = count
    return Vectors.dense(vec)

countsVectors = beatCountsPerYearFull.mapValues(fill_vector)

# Compute correlation matrix
correlation_matrix = Statistics.corr(countsVectors.values())

# Create a mapping of beats to indices
beat_to_index = sc.parallelize(all_beats).zipWithIndex().collectAsMap()
index_to_beat = {v: k for k, v in beat_to_index.items()}

# Create a list to store beat pairs and their correlation
beat_pairs_correlation = []

# Iterate over the correlation matrix
for i in range(correlation_matrix.shape[0]):
    for j in range(i+1, correlation_matrix.shape[1]):  # Only pairs (i, j) with j > i
        beat_pairs_correlation.append((index_to_beat[i], index_to_beat[j], round(correlation_matrix[i][j], 5)))

# Sort the list by correlation in descending order
beat_pairs_correlation.sort(key=lambda x: x[2], reverse=True)

# Write the sorted pairs directly to the final file
with open('beat_correlation_pairs_sorted.txt', 'w') as f:
    for pair in beat_pairs_correlation:
        f.write(f"Correlation between beat {pair[0]} and beat {pair[1]}: {pair[2]}\n")
