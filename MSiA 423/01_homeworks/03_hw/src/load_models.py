# load_models.py
# Import required modules
from pathlib import Path
import logging
import joblib
import boto3
import tempfile

# Set up logging configuration
logger = logging.getLogger("clouds")

# Load your trained models from disk
def load_models(config):
    models = {}
    model_names = config.get('models', {}).keys()
    s3_bucket_name = config.get('aws', {}).get('bucket_name')
    s3_prefix = config.get('aws', {}).get('prefix')
    s3_model_folder = config.get('aws', {}).get('model_folder')

    s3_client = boto3.client('s3')
    try:
        for model_name in model_names:
            s3_model_path = f"{s3_prefix}/{s3_model_folder}{model_name}.pkl"
            with tempfile.TemporaryFile() as fp:
                s3_client.download_fileobj(s3_bucket_name, s3_model_path, fp)
                fp.seek(0)
                model = joblib.load(fp)
                models[model_name] = model
    except Exception as e:
        logger.error(f"Error occurred while loading the models: {e}")
        raise

    if not models:
        logger.error(f"No models found. Raising FileNotFoundError")
        raise FileNotFoundError("No models found. Check config file models & AWS sections.")

    return models
