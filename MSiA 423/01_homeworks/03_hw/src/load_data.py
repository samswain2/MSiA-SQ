# Import required modules
import logging
import pandas as pd

# Set up logging configuration
logger = logging.getLogger("clouds")

# Load features
def load_data(config):
    try:
        data_path = config.get('file_locations', {}).get('data')
        df = pd.read_csv(data_path)
        return df
    except FileNotFoundError:
        logger.error(f"File '{data_path}' not found.")
        raise
    except PermissionError:
        logger.error(f"No permission to read the file '{data_path}'.")
        raise
    except pd.errors.ParserError:
        logger.error(f"Error occurred while parsing the file '{data_path}'.")
        raise
