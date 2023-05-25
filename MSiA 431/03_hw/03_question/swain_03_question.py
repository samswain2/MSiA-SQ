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
spark.sparkContext.setLogLevel("ERROR")  # Reduce console output

# Load and process the crime data
df = spark.read.format("csv").option("header", "true").load(CRIMES_CSV)
df = df.withColumn("Date", to_date(col("Date"), DATE_FORMAT))

# Load and process the IUCR data
other_df = spark.read.format("csv").option("header", "true").load(IUCR_CSV)
other_df = other_df.withColumnRenamed("IUCR", "IUCR_other")

# Join the dataframes
joined_df = df.join(other_df, df.IUCR == other_df.IUCR_other, 'inner')
joined_df = joined_df.withColumn("week_of_year", weekofyear(col("Date")))
joined_df = joined_df.withColumn("year", year(col("Date")))

# Index beat column
indexer = StringIndexer(inputCol="Beat", outputCol="BeatIndex")
joined_df = indexer.fit(joined_df).transform(joined_df)

# Categorize crimes
joined_df = joined_df.withColumn("violent_crime", when(col("PRIMARY DESCRIPTION").isin(VIOLENT_CRIMES), 1).otherwise(0))
joined_df = joined_df.withColumn("non_violent_crime", when(col("PRIMARY DESCRIPTION").isin(NON_VIOLENT_CRIMES), 1).otherwise(0))
joined_df = joined_df.withColumn("Arrest", when(col("Arrest") == True, 1).otherwise(0))
joined_df = joined_df.withColumn("Domestic", when(col("Domestic") == True, 1).otherwise(0))

# Aggregate data
aggregated_df = joined_df.groupBy("Beat", "BeatIndex", "year", "week_of_year")\
    .agg(sql_sum(when(col("violent_crime") == lit(1), 1)).alias("total_violent_crimes"),
         sql_sum(when(col("non_violent_crime") == lit(1), 1)).alias("total_non_violent_crimes"),
         sql_sum(col("Arrest")).alias("total_arrests"),
         sql_sum(col("Domestic")).alias("total_domestic_crimes"),
         countDistinct("District").alias("num_districts"),
         countDistinct("Ward").alias("num_wards"),
         countDistinct("Community Area").alias("num_community_areas"),
         countDistinct("Location Description").alias("num_location_descriptions"))

aggregated_df = aggregated_df.withColumn("total_crimes", col("total_violent_crimes") + col("total_non_violent_crimes"))

# Define a window spec
window_spec = Window.partitionBy('Beat').orderBy('year', 'week_of_year')

# Create lag features
for num_weeks_lag in [1, 2, 3, 4]:
    aggregated_df = aggregated_df.withColumn(f'total_crimes_lag_{num_weeks_lag}', lag('total_crimes', num_weeks_lag).over(window_spec))
    aggregated_df = aggregated_df.withColumn(f'total_arrests_lag_{num_weeks_lag}', lag('total_arrests', num_weeks_lag).over(window_spec))
    aggregated_df = aggregated_df.withColumn(f'total_domestic_crimes_lag_{num_weeks_lag}', lag('total_domestic_crimes', num_weeks_lag).over(window_spec))

# Fill any missing lagged values with 0 (or other value that makes sense in your case)
aggregated_df = aggregated_df.na.fill(0)

# Define columns to be used for training
TRAINING_COLUMNS = [
    # General Info
    'BeatIndex', 
    'year', 
    'week_of_year', 

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

# # Create a comma-separated string of the training columns
# columns_str = ", ".join(TRAINING_COLUMNS)

# # Create a temporary view of the dataframe
# aggregated_df.createOrReplaceTempView("crime_data")

# # Create the SQL query string with the interpolated training columns
# query = f"""
#     SELECT {columns_str}
#     FROM crime_data
#     LIMIT 200
# """

# # Execute the SQL query using spark.sql
# result = spark.sql(query)

# result.show(result.count(), truncate=False)

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
        