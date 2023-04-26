#import libraries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import linear_model, datasets, metrics

## Load .yaml config ##

import yaml

#reading yaml configuration file
with open("../MSIA-SQ/MSiA 423/02_lectures/05_week/model/config.yaml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    print("Read successful")
    print("All data", data)

# import Iris dataset from Scikit-Learn's datasets
iris = datasets.load_iris()

print ("Shape of the data ", iris.data.shape)
print ("Shape of the data ", iris.target_names)
print ("Attributes ", iris.feature_names)

#view first 5 rows
print (iris.data[range(data['show_x_rows'])])
print (iris.target[range(data['show_x_rows'])])

#show it as a table
df = pd.DataFrame(data=iris.data)
df.columns = [iris.feature_names]
df['Class'] = iris.target
df['Name'] = iris.target_names[iris.target]
df.head()


X = iris.data[:, :data['use_first_x_features']]  # we only take the first two features.
Y = iris.target


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=data['test_prop'], random_state=data['random_state'])
X_train.shape, y_train.shape
X_test.shape, y_test.shape


# ### Neural Network using Keras + Tensorflow
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.utils import to_categorical


# Categorical data must be converted to a numerical form. 

def one_hot_encode_object_array(arr):
    '''One hot encode a numpy array of objects (e.g. strings)'''
    uniques, ids = np.unique(arr, return_inverse=True)
    return to_categorical(ids, len(uniques))

y_train_ohe = one_hot_encode_object_array(y_train)
y_test_ohe= one_hot_encode_object_array(y_test)

# Model
model = Sequential()
model.add(Dense(data['model_input_size'], input_shape=(4,)))
model.add(Activation(data['activation_1']))
model.add(Dense(data['output_size']))
model.add(Activation(data['activation_last']))
model.summary()


model.compile(optimizer=data['optimizer'], loss=data['loss'], metrics=[data['metrics']])
model.fit(X_train, y_train_ohe, epochs=data['epochs'], batch_size=data['batch_size'], verbose=data['verbose']);

loss, accuracy = model.evaluate(X_test, y_test_ohe, verbose=data['verbose'])
print("Accuracy = {:.2f}".format(accuracy))

classes = np.argmax(model.predict(X_test), axis=-1)

confusion_matrix =  pd.crosstab(index=y_test, columns=classes.ravel(), rownames=['Expected'], colnames=['Predicted'])
print(confusion_matrix)