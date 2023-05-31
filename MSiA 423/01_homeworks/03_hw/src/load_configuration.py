# Import required modules
import logging
import yaml

# Set up logging configuration
logger = logging.getLogger("clouds")

# Load config
def load_configuration(config_path):
    try:
        with open(config_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        logger.info("Configuration file loaded from %s", config_path)
        return config
    except yaml.error.YAMLError as e:
        logger.error(f"Error while loading configuration from {config_path}: {str(e)}")
        raise
    except FileNotFoundError as e:
        logger.error(f"File {config_path} not found: {str(e)}")
        raise