from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext(appName="myApp")
sc.setLogLevel('ERROR')
sqlcontext = SQLContext(sc)

textFile = sqlcontext.read.csv("hdfs://wolf:9000/user/mtl8754/data/crime/Crimes_-_2001_to_present.csv", header = True)

# counts = textFile.flatMap(lambda line: line.split(" ")).map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)
samples = textFile.sample(.001, False, 42)
# df = samples.toPandas()
# df.to_csv('sample.csv', index = False)
samples.write.option('header', True).csv("hdfs://wolf:9000/user/mtl8754/example/wc_spark/")
