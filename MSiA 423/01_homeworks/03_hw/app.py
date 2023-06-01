import argparse
import logging.config
import yaml

import pandas as pd
import numpy as np
import streamlit as st

from src.load_data import load_data
from src.load_models import load_models
from src.load_configuration import load_configuration

logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger("clouds")

@st.cache_data
def load_config_data_models():
    
    config_path = "config/default-config.yaml"
    config = load_configuration(config_path=config_path)

    df = load_data(config=config)
    logger.info("Loaded data")

    models = load_models(config=config)
    logger.info("Loaded models")

    return config, df, models

def main():
    st.title("Cloud Classification App 🌥️")
    st.write("""
    Welcome to the Cloud Classification App! This application uses machine learning models trained on a cloud dataset 
    from the University of California Irvine machine learning repository. You can select a model to make predictions 
    about cloud type: 0 or 1. Each model requires different inputs, which are all derived from AVHRR images of the 
    clouds. Enjoy exploring!
    """)

    config, df, models = load_config_data_models()

    if not config:
        st.error("Could not load configuration. Please check the logs for more details.")
        return
    
    if df is None or models is None:
        st.error("Could not load data or models. Please check the logs for more details.")
        return

    st.subheader("Model Selection")
    model_choice = st.selectbox("Please select a model:", tuple(models.keys()))
    chosen_model = models[model_choice]
    logger.info("Selected model")

    required_columns = config['models'][model_choice]
    logger.info("Got model's required columns")

    st.subheader("Feature Input")
    user_input = {}
    for feature in required_columns:
        if feature not in df.columns:
            logger.error(f"Feature {feature} not found in the data")
            st.error(f"Feature {feature} not found in the data. Please check your configuration.")
            return

        try:
            min_value = df[feature].min()
            max_value = df[feature].max()
            default_value = (min_value + max_value) / 2.0

            if isinstance(default_value, np.float64):
                default_value = default_value.item()

            user_input[feature] = st.slider(f"Input {feature}:", min_value, max_value, default_value)
            logger.info("Got min, max, and default_value for %s", feature)
        except Exception as e:
            logger.error(f"Error getting values for feature {feature}: {str(e)}")
            st.error(f"Error getting values for feature {feature}. Please check the logs for more details.")
            return

    if st.button("Predict"):
        try:
            data = pd.DataFrame([user_input])
            prediction = chosen_model.predict(data)
            st.write(f"Predicted Cloud Class: {str(prediction[0])}")
            logger.info("Made prediction")
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            st.error("Error making prediction. Please check the logs for more details.")

if __name__ == "__main__":
    main()
