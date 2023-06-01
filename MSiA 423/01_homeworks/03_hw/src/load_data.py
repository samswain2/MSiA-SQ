# load_data.py
# Import required modules
import logging
import pandas as pd
import boto3
from io import StringIO

# Set up logging configuration
logger = logging.getLogger("clouds")

# Load features
def load_data(config):
    try:
        s3_bucket_name = config.get('aws', {}).get('bucket_name')
        s3_prefix = config.get('aws', {}).get('prefix')
        s3_data_file = config.get('aws', {}).get('data_file')
        s3_data_path = f"{s3_prefix}/{s3_data_file}"

        s3_client = boto3.client('s3')

        # Get the CSV data from S3
        csv_obj = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_data_path)
        csv_string = csv_obj['Body'].read().decode('utf-8')

        df = pd.read_csv(StringIO(csv_string))
        return df
    except Exception as e:
        logger.error(f"Error occurred while loading the data: {e}")
        raise
