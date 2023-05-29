from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, row_number, desc, to_timestamp, date_format, when
from pyspark.sql.window import Window
from pyspark.sql.types import FloatType, IntegerType
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
import boto3

### AWS S3 Setup ###
s3 = boto3.client('s3')

data_bucket = 'msia-432-hw4-data'
data_key = 'full_data.csv'


result_bucket = 'sms5736'
result_prefix = '04_hw_431/'
result_key = 'Exercise3.txt'
result_location = result_prefix + result_key

# Start a Spark Session
spark = SparkSession.builder.appName('assignment').getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# Load the data
# df = spark.read.csv(f's3://{data_bucket}/{data_key}', header=True)
df = spark.read.csv('s3://msia-432-hw4-data/full_data.csv', header=True)

# Ensure the data types
df = df.withColumn('trade_id', col('trade_id').cast(IntegerType()))
df = df.withColumn('bar_num', col('bar_num').cast(IntegerType()))
df = df.withColumn('profit', col('profit').cast(FloatType()))

# Drop Rank
df = df.drop('rank')

for i in range(12, 79):  # feature columns
    if f"var{i}" in df.columns:
        df = df.withColumn(f'var{i}', col(f'var{i}').cast(FloatType()))

# Add a column with the bar number relative to the nearest "milestone"
df = df.withColumn("milestone", ((col("bar_num") - 1) / 10).cast(IntegerType()) * 10)

# Calculate the average profit at each milestone
milestone_df = df.filter(col('bar_num') % 10 == 0) \
    .groupBy('trade_id', 'milestone') \
    .agg(F.avg('profit').alias('avg_profit'))

# Increment the milestone by 10 in the milestone_df (since this average will be used for the next milestone)
milestone_df = milestone_df.withColumn('milestone', col('milestone') + 10)

# Join the milestone averages back into the original DataFrame
df = df.join(milestone_df, on=['trade_id', 'milestone'], how='left')

# Forward fill the average profit values for each trade
window_ffill = Window.partitionBy('trade_id').orderBy('bar_num')
df = df.withColumn('avg_profit', F.last('avg_profit', ignorenulls=True).over(window_ffill))

# Sort the data by trade_id and bar_num
window = Window.orderBy(desc('trade_id'), col('bar_num'))
df = df.withColumn('rank', row_number().over(window))

window_lag = Window.partitionBy('trade_id').orderBy('bar_num')

# # Get lag profits
# for i in range(11, 20):  # lag profits for last 10 bars
#     df = df.withColumn(f'profit_lag_{i}', lag('profit', offset=i).over(window_lag))

# Get lag vars
for lag_offset in range(1, 7):
    for var_num in range(12, 79):  # feature columns
        var = f"var{var_num}"
        if var in df.columns:
            df = df.withColumn(f'var{var_num}_lag{lag_offset}', lag(var, offset=lag_offset).over(window_lag))

# drop null values (i.e., the first 10 rows for each trade_id, as they don't have complete lag features)
df = df.dropna()

# Drop temporary milestone column
df = df.drop('milestone')

# Convert the date column into timestamp
df = df.withColumn('date', to_timestamp('time_stamp', 'yyyy-MM-dd HH:mm:ss'))

# Extract year-month from date
df = df.withColumn('year_month', date_format('time_stamp', 'yyyy-MM'))

# Generate the list of unique year-months
year_months = df.select('year_month').distinct().rdd.flatMap(lambda x: x).collect()
year_months.sort()

# Defining the input columns for the vector assembler
input_cols = df.columns
input_cols.remove('time_stamp')
input_cols.remove('bar_num')
input_cols.remove('direction')
input_cols.remove('trade_id')
input_cols.remove('rank')
input_cols.remove('date')
input_cols.remove('year_month')
input_cols.remove('profit')  # assuming 'profit' is the name of your target variable

# Initialize the Vector Assembler
assembler = VectorAssembler(inputCols=input_cols, outputCol='features')

# Define your model as RandomForestRegressor
rf = RandomForestRegressor(labelCol='profit', featuresCol='features')

# Define your evaluator for RMSE and R-Squared
evaluator_rmse = RegressionEvaluator(labelCol='profit', metricName="rmse")
evaluator_r2 = RegressionEvaluator(labelCol='profit', metricName="r2")

# Init storage results lists
r2_values = []
mape_values = []
output = ''

for i in range(0, len(year_months)-6, 7):
    # Get the train and test data
    train_data = df.filter(df.year_month.isin(year_months[i:i+6]))
    test_data = df.filter(df.year_month == year_months[i+6])
    
    # Transform the data
    train_data = assembler.transform(train_data)
    test_data = assembler.transform(test_data)

    # Train your model
    rf_model = rf.fit(train_data)
    
    # Perform inference on the test data
    predictions = rf_model.transform(test_data)
    
    # Evaluate your predictions and store the RMSE and R-Squared result for later analysis
    rmse = evaluator_rmse.evaluate(predictions)
    r2 = evaluator_r2.evaluate(predictions)
    
    # Compute MAPE and store it for later analysis
    mape = predictions.select(F.avg(F.abs((predictions['profit'] - predictions['prediction']) / predictions['profit']))).alias('mape').collect()[0][0]
    
    # Write the range of the training timeframe, RMSE, R-squared and MAPE for the current timeframe to file
    output += f'Training timeframe: {year_months[i]} to {year_months[i+5]}\n'
    output += '----------------------------------\n'
    output += f'The RMSE for year-month {year_months[i+6]} is {rmse}\n'
    output += f'The R-squared for year-month {year_months[i+6]} is {r2}\n'
    output += f'The MAPE for year-month {year_months[i+6]} is {mape}\n'
    output += f'\n'

# Calculate and write overall R-squared, average MAPE, max MAPE and min MAPE to file
overall_r2 = sum(r2_values) / len(r2_values)
avg_mape = sum(mape_values) / len(mape_values)
max_mape = max(mape_values)
min_mape = min(mape_values)
output += f'Overall Results\n'
output += f'----------------------------------\n'
output += f'The overall R-squared value: {overall_r2}\n'
output += f'The average MAPE score: {avg_mape}\n'
output += f'The maximum MAPE score: {max_mape}\n'
output += f'The minimum MAPE score: {min_mape}\n'

# Upload the file
s3.put_object(Body=output, Bucket=result_bucket, Key=result_key)