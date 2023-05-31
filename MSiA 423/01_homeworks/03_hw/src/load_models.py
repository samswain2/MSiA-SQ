# Import required modules
from pathlib import Path
import logging
import joblib

# Set up logging configuration
logger = logging.getLogger("clouds")

# Load your trained models from disk
def load_models(config):
    models = {}
    model_names = config.get('models', {}).keys()
    model_folder = config.get('file_locations', {}).get('models')

    for model_name in model_names:
        model_path = Path(f'{model_folder}/{model_name}.pkl')
        try:
            model = joblib.load(model_path)
            models[model_name] = model
        except FileNotFoundError:
            logger.error(f"Model file {model_path} not found.")
        except EOFError:
            logger.error(f"Model file {model_path} is empty or corrupted.")
        except OSError:
            logger.error(f"Model file {model_path} is not readable or corrupted.")

    if not models:
        logger.error(f"No models found. Raising FileNotFoundError")
        raise FileNotFoundError("No models found. Check config file models & file_locations sections.")

    return models


