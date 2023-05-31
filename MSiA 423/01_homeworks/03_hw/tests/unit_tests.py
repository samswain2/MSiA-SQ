import pytest
import pandas as pd
import yaml
from unittest import mock
from unittest.mock import Mock

from src.app import load_configuration, load_data_and_models
from src.load_data import load_data
from src.load_models import load_models

def test_load_configuration():
    with mock.patch('builtins.open', mock.mock_open(read_data="models:")):
        config = load_configuration("fake/path")
        assert config == {"models": {}}

def test_load_configuration_invalid_yaml():
    with mock.patch('builtins.open', mock.mock_open(read_data="models")):
        with pytest.raises(yaml.YAMLError):
            load_configuration("fake/path")

def test_load_configuration_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_configuration("nonexistent/path")

def test_load_data_and_models_no_config():
    with pytest.raises(TypeError):
        load_data_and_models(None)

@mock.patch('src.load_data.load_data')
@mock.patch('src.load_models.load_models')
def test_load_data_and_models(mock_load_models, mock_load_data):
    mock_load_data.return_value = pd.DataFrame()
    mock_load_models.return_value = {"model1": Mock()}

    df, models = load_data_and_models({"fake_config": True})

    assert isinstance(df, pd.DataFrame)
    assert isinstance(models, dict)

@mock.patch('src.load_data.load_data', side_effect=Exception('fake error'))
def test_load_data_and_models_data_exception(mock_load_data):
    with pytest.raises(Exception):
        load_data_and_models({"fake_config": True})

@mock.patch('src.load_data.load_data')
@mock.patch('src.load_models.load_models', side_effect=Exception('fake error'))
def test_load_data_and_models_models_exception(mock_load_models, mock_load_data):
    mock_load_data.return_value = pd.DataFrame()
    with pytest.raises(Exception):
        load_data_and_models({"fake_config": True})
        