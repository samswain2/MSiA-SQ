import numpy as np
import pandas as pd
import requests



columns = ['visible_mean', 'visible_max', 'visible_min', 
           'visible_mean_distribution', 'visible_contrast', 
           'visible_entropy', 'visible_second_angular_momentum', 
           'IR_mean', 'IR_max', 'IR_min']

url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/undocumented/taylor/cloud.data'
response = requests.get(url)
data = response.text


# First Cloud Class
first_row_first_cloud, last_row_first_cloud = 53, 1076

first_cloud = data[first_row_first_cloud:last_row_first_cloud]

first_cloud = [[float(s.replace('/n', '')) for s in cloud]
                for cloud in first_cloud]
first_cloud = pd.DataFrame(first_cloud, columns=columns)

first_cloud['class'] = np.zeros(len(first_cloud))

# Second Cloud Class
