from pyspark import SparkContext, SparkConf
from datetime import datetime
from math import sqrt
from scipy import stats

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
    district = fields[11]
    return (district, date)

# Parse the RDD
crimeDataParsed = crimeData.map(parse)

# Filter for the time during which each mayor was in office
dalyCrimes = crimeDataParsed.filter(lambda x: datetime(1989, 4, 24) <= x[1] <= datetime(2011, 5, 16))
emanuelCrimes = crimeDataParsed.filter(lambda x: datetime(2011, 5, 16) < x[1] <= datetime(2019, 5, 20))

# Filter out non-numeric districts
dalyCrimes = dalyCrimes.filter(lambda x: x[0].isdigit())
emanuelCrimes = emanuelCrimes.filter(lambda x: x[0].isdigit())

# Filter out districs out of the range 1 to 25s
extra_districts = [13, 21, 23]
dalyCrimes = dalyCrimes.filter(lambda x: 25 >= int(x[0]) >= 1 and int(x[0]) not in extra_districts)
emanuelCrimes = emanuelCrimes.filter(lambda x: 25 >= int(x[0]) >= 1 and int(x[0]) not in extra_districts)

# Set each observation with a value of 1
dalyCrimes = dalyCrimes.map(lambda x: (x[0], 1))
emanuelCrimes = emanuelCrimes.map(lambda x: (x[0], 1))

# Calculate sum and count for each block during each mayor's term
def seqOp(x, y):
    return (x[0] + y, x[1] + 1)

def combOp(x, y):
    return (x[0] + y[0], x[1] + y[1])

zeroValue = (0, 0)

dalyBlockStats = dalyCrimes.aggregateByKey(zeroValue, seqOp, combOp)
emanuelBlockStats = emanuelCrimes.aggregateByKey(zeroValue, seqOp, combOp)

# Calculate total crimes and total districts for each mayor's term
totalCrimesDaly = dalyBlockStats.map(lambda x: x[1][0]).sum()
totalDistrictsDaly = dalyBlockStats.count()

totalCrimesEmanuel = emanuelBlockStats.map(lambda x: x[1][0]).sum()
totalDistrictsEmanuel = emanuelBlockStats.count()

# Calculate mean for each mayor's term
meanDaly = totalCrimesDaly / totalDistrictsDaly
meanEmanuel = totalCrimesEmanuel / totalDistrictsEmanuel

# Calculate variance for each mayor's term
varDaly = dalyBlockStats.map(lambda x: (x[1][0] - meanDaly) ** 2).sum() / totalDistrictsDaly
varEmanuel = emanuelBlockStats.map(lambda x: (x[1][0] - meanEmanuel) ** 2).sum() / totalDistrictsEmanuel

# Calculate standard deviation for each mayor's term
sdDaly = sqrt(varDaly)
sdEmanuel = sqrt(varEmanuel)

# Calculate the t-statistic
t = abs((meanDaly - meanEmanuel) / sqrt((sdDaly**2/totalDistrictsDaly) + (sdEmanuel**2/totalDistrictsEmanuel)))

# Calculate degrees of freedom
df = totalDistrictsDaly + totalDistrictsEmanuel - 2

# Calculate the p-value
p = stats.t.sf(t, df)

# Save the mean, standard deviation, t-statistic, and p-value for each mayor's term
with open('mean_sd_t_stat_p_value.txt', 'w') as f:
    f.write(f"Mayor Daly (Districts): Mean = {meanDaly}, SD = {sdDaly}\n")
    f.write(f"Mayor Emanuel (Districts): Mean = {meanEmanuel}, SD = {sdEmanuel}\n")
    f.write(f"T-statistic for difference in means: {t}\n")
    f.write(f"P-value for difference in means: {p}\n")
