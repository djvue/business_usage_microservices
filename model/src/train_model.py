import pickle
import pandas as pd

from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
 
diabetes = load_diabetes()

X = diabetes.data
y = diabetes.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state=0)
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred = lr.predict(X_test)

r2_score = r2_score(y_test, y_pred)
print("R2 score", r2_score)
 
# Читаем файл с сериализованной моделью
with open('data/model.pkl', 'wb') as pkl_file:
    pickle.dump(lr, pkl_file)
