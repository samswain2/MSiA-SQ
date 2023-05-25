from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, col, weekofyear, year, lit, count, when, countDistinct, sum as sql_sum
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import RandomForestRegressor, GBTRegressor, LinearRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql import Window
from pyspark.sql.functions import lag

# Define constants
APP_NAME = "Chicago Crime Analysis"
CRIMES_CSV = "hdfs:///user/sms5736/03_hw/Crimes_-_2001_to_present.csv"
IUCR_CSV = "hdfs:///user/sms5736/03_hw/IUCR.csv"
STOCK_CSV = "hdfs:///user/sms5736/03_hw/combined_sp500.csv"
DATE_FORMAT = 'MM/dd/yyyy hh:mm:ss a'

# Define Violent and Non-Violent Crimes
VIOLENT_CRIMES = ["OFFENSE INVOLVING CHILDREN", "PUBLIC PEACE VIOLATION", "ARSON", "ASSAULT", "BATTERY", "ROBBERY",
                  "HUMAN TRAFFICKING", "SEX OFFENSE", "CRIMINAL DAMAGE", "KIDNAPPING",
                  "INTERFERENCE WITH PUBLIC OFFICER"]

NON_VIOLENT_CRIMES = ["OBSCENITY", "OTHER OFFENSE", "GAMBLING", "CRIMINAL TRESPASS", "LIQUOR LAW VIOLATION",
                      "PUBLIC INDECENCY", "INTIMIDATION", "PROSTITUTION", "DECEPTIVE PRACTICE",
                      "CONCEALED CARRY LICENSE VIOLATION", "NARCOTICS", "NON-CRIMINAL", "WEAPONS VIOLATION",
                      "OTHER NARCOTIC VIOLATION"]

# Start Spark session
spark = SparkSession.builder.appName(APP_NAME).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Load and process datasets
crime_df = spark.read.csv(CRIMES_CSV, header=True)
crime_df = crime_df.withColumn("Date", to_date(col("Date"), DATE_FORMAT))

iucr_df = spark.read.csv(IUCR_CSV, header=True)
iucr_df = iucr_df.withColumnRenamed("IUCR", "IUCR_other")

stock_df = spark.read.csv(STOCK_CSV, header=True)
stock_df = stock_df.withColumn("Date", to_date(col("Date"), 'yyyy-MM-dd'))
stock_df = stock_df.withColumn("Close", col("Close").cast("float"))
stock_df = stock_df.withColumn("week_of_year", weekofyear(col("Date")))
stock_df = stock_df.withColumn("year", year(col("Date")))

# Compute average weekly closing price
weekly_stock_df = stock_df.groupBy("year", "week_of_year").avg("Close")
weekly_stock_df = weekly_stock_df.withColumnRenamed("avg(Close)", "avg_weekly_close")
weekly_stock_df = weekly_stock_df.withColumn('avg_weekly_close_lag_1', lag('avg_weekly_close', 1).over(Window.orderBy('year', 'week_of_year')))
weekly_stock_df = weekly_stock_df.withColumn('weekly_close_change', (col('avg_weekly_close') - col('avg_weekly_close_lag_1')) / col('avg_weekly_close_lag_1') * 100)
weekly_stock_df = weekly_stock_df.na.fill(0)

# Merge datasets and feature engineering
joined_df = crime_df.join(iucr_df, crime_df.IUCR == iucr_df.IUCR_other, 'inner')
joined_df = joined_df.withColumn("week_of_year", weekofyear(col("Date")))
joined_df = joined_df.withColumn("year", year(col("Date")))
joined_df = joined_df.join(weekly_stock_df, ['year', 'week_of_year'], 'inner')

indexer = StringIndexer(inputCol="Beat", outputCol="BeatIndex")
joined_df = indexer.fit(joined_df).transform(joined_df)

joined_df = joined_df.withColumn("violent_crime", when(col("PRIMARY DESCRIPTION").isin(VIOLENT_CRIMES), 1).otherwise(0))
joined_df = joined_df.withColumn("non_violent_crime", when(col("PRIMARY DESCRIPTION").isin(NON_VIOLENT_CRIMES), 1).otherwise(0))
joined_df = joined_df.withColumn("Arrest", when(col("Arrest") == True, 1).otherwise(0))
joined_df = joined_df.withColumn("Domestic", when(col("Domestic") == True, 1).otherwise(0))

# Aggregate data
aggregated_df = joined_df.groupBy("Beat", "BeatIndex", "year", "week_of_year", "avg_weekly_close", "weekly_close_change") \
    .agg(sql_sum(when(col("violent_crime") == lit(1), 1)).alias("total_violent_crimes"),
         sql_sum(when(col("non_violent_crime") == lit(1), 1)).alias("total_non_violent_crimes"),
         sql_sum(col("Arrest")).alias("total_arrests"),
         sql_sum(col("Domestic")).alias("total_domestic_crimes"),
         countDistinct("District").alias("num_districts"),
         countDistinct("Ward").alias("num_wards"),
         countDistinct("Community Area").alias("num_community_areas"),
         countDistinct("Location Description").alias("num_location_descriptions"))

aggregated_df = aggregated_df.withColumn("total_crimes", col("total_violent_crimes") + col("total_non_violent_crimes"))

# Lag features and fill NA
window_spec = Window.partitionBy('Beat').orderBy('year', 'week_of_year')

for num_weeks_lag in [1, 2, 3, 4]:
    aggregated_df = aggregated_df.withColumn(f'total_crimes_lag_{num_weeks_lag}', lag('total_crimes', num_weeks_lag).over(window_spec))
    aggregated_df = aggregated_df.withColumn(f'total_arrests_lag_{num_weeks_lag}', lag('total_arrests', num_weeks_lag).over(window_spec))
    aggregated_df = aggregated_df.withColumn(f'total_domestic_crimes_lag_{num_weeks_lag}', lag('total_domestic_crimes', num_weeks_lag).over(window_spec))

aggregated_df = aggregated_df.na.fill(0)

# Define columns to be used for training
TRAINING_COLUMNS = [
    # General Info
    'BeatIndex', 
    'year', 
    'week_of_year', 

    # Stock Info
    'avg_weekly_close',
    'weekly_close_change',

    # Data Leakage:
    # 'total_arrests',
    # 'total_domestic_crimes', 

    # Location Information
    'num_districts', 
    'num_wards', 
    'num_community_areas', 
    'num_location_descriptions',

    # Lag features
    'total_crimes_lag_1',
    'total_arrests_lag_1',
    'total_domestic_crimes_lag_1',
    'total_crimes_lag_2',
    'total_arrests_lag_2',
    'total_domestic_crimes_lag_2',
    'total_crimes_lag_3',
    'total_arrests_lag_3',
    'total_domestic_crimes_lag_3',
    'total_crimes_lag_4',
    'total_arrests_lag_4',
    'total_domestic_crimes_lag_4'
]

# Assemble the features into a feature vector
assembler = VectorAssembler(inputCols=TRAINING_COLUMNS, outputCol="features")

# Define the models
rf = RandomForestRegressor(labelCol="total_crimes", featuresCol="features")
gbt = GBTRegressor(labelCol="total_crimes", featuresCol="features")
lr = LinearRegression(labelCol="total_crimes", featuresCol="features")

# Create pipelines for the models
pipeline_rf = Pipeline(stages=[assembler, rf])
pipeline_gbt = Pipeline(stages=[assembler, gbt])
pipeline_lr = Pipeline(stages=[assembler, lr])

# Split the data
(training_data, test_data) = aggregated_df.randomSplit([0.8, 0.2], seed=1234)

# Persist training and testing data
training_data.persist()
test_data.persist()

# Train and evaluate the models
with open('model_results.txt', 'w') as f:
    for name, pipeline in [('Random Forest', pipeline_rf), ('Gradient-Boosted Tree', pipeline_gbt), ('Linear Regression', pipeline_lr)]:
        model = pipeline.fit(training_data)
        predictions = model.transform(test_data)
        evaluator = RegressionEvaluator(labelCol="total_crimes", predictionCol="prediction")
        rmse = evaluator.setMetricName("rmse").evaluate(predictions)
        r2 = evaluator.setMetricName("r2").evaluate(predictions)
        mae = evaluator.setMetricName("mae").evaluate(predictions)

        # Save the models' predictions
        f.write(f"{name}:\n")
        f.write(f"RMSE: {rmse}\n")
        f.write(f"R-squared: {r2}\n")
        f.write(f"Mean Absolute Error (as proxy for MAPE): {mae}\n\n")
