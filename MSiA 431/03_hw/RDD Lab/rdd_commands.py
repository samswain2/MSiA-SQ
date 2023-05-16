sc.setLogLevel("Error")
myRDD = sc.parallelize([1,2,3,4,5],2)
myRDD.collect()

myRDD.getNumPartitions()

myRDD.count()

myRDD.map(lambda x: x+1)

tempRDD = myRDD.map(lambda x: x+1)

tempRDD

myRDD.map(lambda x: x+1).collect()

def f(x): return x+1

myRDD.map(f).collect()

myRDD.take(2)

myRDD.take(5)

myRDD.reduce(lambda x,y: x+y)

myRDD = sc.textFile('hdfs://wolf:9000/user/mtl8754/data/spark/bees.txt')

myRDD.map(lambda x:x.split(" ")).collect()

myRDD.map(lambda x:x.split(" ")).take(2)

myRDD.take(2)

myRDD.flatMap(lambda x:x.split(" ")).take(2)

myRDD.flatMap(lambda x:x.split(" ")).map(lambda x: (x,1)).take(2)

myRDD.flatMap(lambda x:x.split(" ")).map(lambda x: (x,1)).reduceByKey(lambda a,b: a+b).take(10)

sc.textFile('hdfs://wolf:9000/user/mtl8754/data/spark/bees.txt').flatMap(lambda x:x.split(" ")).map(lambda x: (x,1)).reduceByKey(lambda a,b: a+b).take(10)

myRDD = sc.textFile('hdfs://wolf:9000/user/mtl8754/data/spark/pairs.txt')

myRDD.take(2)

myRDD.map(lambda x: x.split(" ")).collect()

myRDD.map(lambda x: x.split(" ")).toDF().show()

df = myRDD.map(lambda x: x.split(" ")).toDF(['toy', 'count'])

df.show()

