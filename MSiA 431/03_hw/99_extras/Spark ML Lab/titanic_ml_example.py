from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import StringIndexer, VectorIndexer, OneHotEncoder, VectorAssembler, IndexToString
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import *
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import Imputer

spark = SparkSession \
    .builder \
    .appName("randomSample") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

titanic_path = 'hdfs://wolf:9000/user/mtl8754/data/titanic/titanic_train.csv'
titanic = spark.read.csv(titanic_path, header = True)
print('file_read')


titanic = titanic.withColumn("Embarked", 
                             when(col('Embarked') == '', "C")\
                             .otherwise(col('Embarked')))

#NOT mllib

titanic = titanic.withColumn("Age", titanic["Age"].cast(DoubleType()))

#Fill empty ages with the mean age of all passengers, rather than remove the nulls
imputer = Imputer(
    inputCols=['Age'],
    outputCols=["new_Age"]
)
titanic = imputer.setStrategy("mean").fit(titanic).transform(titanic)

from pyspark.sql.functions import *

#Extracting Titles from a String with regex
titanic_titles = titanic.withColumn("Title", regexp_replace(col('Name'), '(.*, )|(\\..*)', ''))

#Create lists of title groups which are uncommon
rare_title = ['Dona', 'Lady', 'the Countess', 'Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer']
Miss = ['Mlle', 'Ms']

#Creating the column
titanic_titles = titanic_titles.withColumn("Title", \
                                          when(col('Title').isin(rare_title), "Rare Title")\
                                          .when(col('Title').isin(Miss), "Miss")\
                                          .when(col('Title') == "Mme", "Mrs")\
                                          .otherwise(titanic_titles.Title))

titanic_age_bin = titanic_titles.withColumn("Child", \
                                           when(col('new_Age') < 18, "Child")\
                                            # when(expr("new_Age < 18"), "Child")
                                           .otherwise("Adult"))

#Mother, Family Size

titanic_mom = titanic_age_bin.withColumn("Mother", \
                                         when(expr("Sex == 'female' AND new_Age > 18 AND Parch > 0"), "Mother")
#                                            when((col('Sex') == 'female') & (col('Age') > 18) & (col('Parch') > 0), "Mother")\
                                           .otherwise("Non-Mother"))

titanic_parent = titanic_mom.withColumn("A-Parent", \
                                          when((col('Parch') > 0) & (col('Age')>18), "A_Parent")\
                                          .otherwise("Non-Parent"))

#Family Sizes
titanic_famSize = titanic_parent.withColumn("Fsize", \
                                            col('SibSp') + col('Parch') +1)

titanic_f = titanic_famSize.withColumn("FsizeD", \
                                         when(col('Fsize')==1, "single")\
                                         .when((col('Fsize') < 5) & (col('Fsize') > 1), "medium")\
                                         .otherwise("large"))

#Dataset from before any indexing or encoding happened
titanic_final = titanic_f.select("Survived", "Pclass", "Sex", "new_Age", "A-Parent", "FsizeD", "Title")
print('done with transformations')

classIdxer = StringIndexer(inputCol='Pclass',outputCol='PclassIdx')
sexIdxer = StringIndexer(inputCol='Sex',outputCol='SexIdx')
parentIdxer = StringIndexer(inputCol='A-Parent',outputCol='A-ParentIdx')
FsizeIdxer = StringIndexer(inputCol='FsizeD',outputCol='FsizeDIdx')
titleIdxer = StringIndexer(inputCol='Title',outputCol='TitleIdx')

survivedIdxer = StringIndexer(inputCol="Survived", outputCol="SurvivedIdx")

encoder = OneHotEncoder(inputCols=["PclassIdx", "SexIdx", "A-ParentIdx", "FsizeDIdx", "TitleIdx"], outputCols=["Pclassvec", "Sexvec", "A-Parentvec", "FsizeDvec", "Titlevec"]).setHandleInvalid("keep")

assembler = VectorAssembler(inputCols = ["Pclassvec", "Sexvec", "new_Age", "A-Parentvec", "FsizeDvec", "Titlevec"], outputCol = 'features')

rf = RandomForestClassifier(labelCol="SurvivedIdx", featuresCol="features")

pipeline = Pipeline(stages = [classIdxer, sexIdxer, parentIdxer, FsizeIdxer, titleIdxer, survivedIdxer, encoder, assembler, rf])

train, test = titanic_final.randomSplit([0.75, 0.25])

model = pipeline.fit(train)
predictions = model.transform(test)
print('model transformed')

predictions2 = predictions.select(col("Survived").cast("Float"),col("prediction"))
evaluator = MulticlassClassificationEvaluator(labelCol="Survived", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions2)
print("Test Error = %g" % (1.0 - accuracy))

predictions.createOrReplaceTempView("Predictions")
predictions_sql = spark.sql("select sum(case when SurvivedIdx = prediction then 1 else 0 end) / count(prediction) as Accuracy from Predictions")

with open('titanic_accuracy.txt', 'w') as file:
    for item in predictions_sql.collect():
        file.write(str(item))

spark.sparkContext.stop()