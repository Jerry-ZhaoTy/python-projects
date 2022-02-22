# project: p7
# submitter: tzhao86
# partner: none
# hours: 10


import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.compose import make_column_transformer


class UserPredictor:
    
    def __init__(self):
        self.xcols = ["age","past_purchase_amt","total_time","total_time_laptop","badge"]
        
    def fit(self, users, logs, y):
        users['y'] = y['y']
        users.set_index('user_id', drop = False, inplace = True)
        users['total_time'] = pd.DataFrame(logs.groupby(['user_id'])['seconds'].sum())
        logs = logs[logs["url"] == "/laptop.html"]
        users['total_time_laptop'] = pd.DataFrame(logs.groupby(['user_id'])['seconds'].sum())
        users = users.dropna(axis = 0)
        combined = make_column_transformer(
            (PolynomialFeatures(degree=3, include_bias = False), ["age", "past_purchase_amt","total_time"]),
            (OneHotEncoder(), ["badge"]),
        )
        self.model = Pipeline([
            ("trans", combined), 
            ("std", StandardScaler()),
            ("lr", LogisticRegression(max_iter = 200)),
         ])
        self.model.fit(users[self.xcols], users["y"])
        
    def predict(self, users, logs):
        users.set_index('user_id', drop = False, inplace = True)
        users['total_time'] = pd.DataFrame(logs.groupby(['user_id'])['seconds'].sum())
        logs = logs[logs["url"] == "/laptop.html"]
        users['total_time_laptop'] = pd.DataFrame(logs.groupby(['user_id'])['seconds'].sum())
        users = users.fillna(-1)
        return self.model.predict(users[self.xcols])
    


