# PySpark Regression Analysis with AWS S3
This Python script conducts an analysis of a dataset stored on an AWS S3 bucket, utilizing PySpark to implement a Random Forest Regression model to predict profits.

## Table of Contents
- [AWS S3 Setup](#aws-s3-setup)
- [Spark Session Initialization](#spark-session-initialization)
- [Data Loading and Preprocessing](#data-loading-and-preprocessing)
- [Feature Engineering](#feature-engineering)
- [Model Training and Evaluation](#model-training-and-evaluation)
- [Results Output](#results-output)

## AWS S3 Setup
The initial segment of this script is dedicated to setting up AWS S3. It utilizes boto3 to establish a connection with AWS S3 and define the location of the dataset we're going to analyze. Moreover, it also sets up the location where we will save the output of our analysis.

## Spark Session Initialization
In the following segment, we initialize a Spark Session, which will be used for data loading and transformation. We also set the log level to ERROR to filter out redundant log messages, focusing on error messages only.

## Data Loading and Preprocessing
Next, the script handles data loading and preprocessing. It retrieves data directly from the S3 bucket and loads it into a PySpark DataFrame. During the loading process, the script ensures the data types are correctly defined. Further preprocessing includes dropping the 'rank' column and casting specific columns to appropriate data types. The script also adds a new column 'milestone', giving us insight into the progress of bars relative to the nearest "milestone".

## Feature Engineering
In the feature engineering stage, the script adds a series of new features to our DataFrame. One important step is calculating the average profit at each milestone and joining it back to the original DataFrame. It also uses forward fill to populate null values in the average profit column. Additional features include sorting the data by 'trade_id' and 'bar_num' and creating lagged features for each variable. After the feature engineering process, the script removes any rows with null values and converts 'time_stamp' into datetime format. The 'year_month' is then extracted from this converted 'time_stamp'.

## Model Training and Evaluation
The model training and evaluation section is where the magic happens. First, the script defines the input columns for the Vector Assembler. With these inputs, the Vector Assembler is initialized, which transforms the data into a format suitable for the machine learning model. A Random Forest Regressor model is then defined and prepared for training. Evaluation metrics, Root Mean Squared Error (RMSE), and R-squared, are also defined at this point. In the training loop, the script prepares training and test datasets, fits the model on the training data, and makes predictions on the test data. Each loop iteration calculates and stores the RMSE, R-squared, and Mean Absolute Percentage Error (MAPE).

## Results Output
Finally, the results output section calculates overall R-squared, average MAPE, max MAPE, and min MAPE from the previously stored evaluation metrics. The evaluation results are written into a text file. Lastly, this results file is uploaded back to the specified S3 bucket, serving as the final output of our script.

Please note that each step of the script is thoroughly commented in the code, providing a more detailed explanation.