from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, col, weekofyear, year, lit, count, when, countDistinct, sum as sql_sum, lpad, monotonically_increasing_id
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import RandomForestRegressor, GBTRegressor, LinearRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql import Window
from pyspark.sql.functions import lag
from fairlearn.metrics import MetricFrame
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import pandas as pd

# Define constants
APP_NAME = "Chicago Crime Analysis"
CRIMES_CSV = "hdfs:///user/sms5736/03_hw/Crimes_-_2001_to_present.csv"
IUCR_CSV = "hdfs:///user/sms5736/03_hw/IUCR.csv"
STOCK_CSV = "hdfs:///user/sms5736/03_hw/combined_sp500.csv"
DEMOGRAPHIC_CSV = "hdfs:///user/sms5736/03_hw/demographic_data.csv"
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

# Load in demographic data
demographic_df = spark.read.csv(DEMOGRAPHIC_CSV, header=True)
demographic_df = demographic_df.withColumn("beat", lpad(col("beat"), 4, '0'))

# Convert all demographic numerical columns to float type
for col_name in demographic_df.columns:
    if col_name != 'beat':
        demographic_df = demographic_df.withColumn(col_name, col(col_name).cast('float'))

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

aggregated_df = aggregated_df.join(demographic_df, aggregated_df.Beat == demographic_df.beat, 'inner')

# Fill nas with 0
aggregated_df = aggregated_df.na.fill(0)

# Convert Spark DataFrame to Pandas DataFrame
pandas_df = aggregated_df.toPandas()

# # Print df columns
# for col in pandas_df.columns:
#     print(col)

# Define columns to be used for training
TRAINING_COLUMNS = [
    # General Info
    'BeatIndex', 
    'year', 
    'week_of_year', 

    # Stock Info
    'avg_weekly_close',
    'weekly_close_change',

    # Demographic Info
    'num_white',
    'num_hispanic',
    'num_black',
    'num_asian',
    'num_mixed',
    'num_other',
    'bachelors',
    'high_school',
    'no_high_school',
    'population',
    'med_income',

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

# Convert test data to pandas
pandas_test_data = test_data.toPandas()

# Use the correct length for sensitive_features
sensitive_features = pandas_test_data['med_income']

# Define the income groups
income_bins = [0, 25000, 50000, 75000, 100000, float('inf')]
income_labels = ['$0 - $25k', '$25k - $50k', '$50k - $75k', '$75k - $100k', '> $100k']

# Create dictionaries to store income and MSE values
income_values = {}
mse_values = {}

# Bin the income into groups first
sensitive_features_binned = pd.cut(sensitive_features, bins=income_bins, labels=income_labels, right=False)

# Train and evaluate the models
with open('swain_03_output_models.txt', 'w') as f, open('swain_03_output_bias.txt', 'w') as bias_f:
    for name, pipeline in [('RF', pipeline_rf), ('GBT', pipeline_gbt), ('LR', pipeline_lr)]:
        model = pipeline.fit(training_data)
        predictions = model.transform(test_data)

        # Convert to pandas
        pandas_predictions = predictions.toPandas()["prediction"].values
        pandas_labels = predictions.toPandas()["total_crimes"].values

        # Compute mean_squared_error for each group defined by the sensitive feature
        metric_frame = MetricFrame(metrics=mean_squared_error, y_true=pandas_labels, y_pred=pandas_predictions, sensitive_features=sensitive_features_binned)

        # Sort by index (income bins)
        sorted_group_metrics = metric_frame.by_group.sort_index()

        # Store income and MSE values in dictionaries
        income_values[name] = sorted_group_metrics.index
        mse_values[name] = sorted_group_metrics.values

        # Plotting
        plt.bar(income_values[name], mse_values[name], label=name)  # Bar plot instead of line plot
        plt.xlabel('Income')
        plt.ylabel('Mean Squared Error')
        plt.title(name)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.legend()
        plt.savefig(f'swain_{name}_hist.png')  # Save the plot as an image
        plt.close()  # Close the plot to clear the figure for the next iteration

        # Overall metric
        bias_f.write(f"Overall fairness metrics for {name}:\n")
        bias_f.write(str(metric_frame.overall))
        bias_f.write("\n\n")

        # Metric per-group
        bias_f.write(f"Binned per-group fairness metrics for {name}:\n")
        bias_f.write(str(sorted_group_metrics))  # Save sorted binned results instead of raw metrics
        bias_f.write("\n")

        evaluator = RegressionEvaluator(labelCol="total_crimes", predictionCol="prediction")
        rmse = evaluator.setMetricName("rmse").evaluate(predictions)
        r2 = evaluator.setMetricName("r2").evaluate(predictions)
        mae = evaluator.setMetricName("mae").evaluate(predictions)

        # Save the models' predictions
        f.write(f"{name}:\n")
        f.write(f"RMSE: {rmse}\n")
        f.write(f"R-squared: {r2}\n")
        f.write(f"Mean Absolute Error (as proxy for MAPE): {mae}\n\n")
