import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import joblib
import os

class TreinadorModelo:
    def __init__(self):
        self.model_file = "modelo.pkl"
        self.scaler_file = "scaler.pkl"
        self.load()

    def load(self):
        if os.path.exists(self.model_file):
            self.model = joblib.load(self.model_file)
            self.scaler = joblib.load(self.scaler_file)
        else:
            self.model = None
            self.scaler = MinMaxScaler()

    def salvar(self):
        joblib.dump(self.model, self.model_file)
        joblib.dump(self.scaler, self.scaler_file)

    def resetar(self):
        if os.path.exists(self.model_file):
            os.remove(self.model_file)
        if os.path.exists(self.scaler_file):
            os.remove(self.scaler_file)
        self.model = None
        self.scaler = MinMaxScaler()

    def treinar(self, df):
        y = df["time"]
        X = df.drop("time", axis=1)

        X_scaled = self.scaler.fit_transform(X)

        self.model = LinearRegression()
        self.model.fit(X_scaled, y)

        pred = self.model.predict(X_scaled)
        mse = mean_squared_error(y, pred)

        return mse

    def testar(self, df, tem_rotulos):
        X = df.drop(columns=["time"], errors="ignore")
        X_scaled = self.scaler.transform(X)

        preds = pd.DataFrame({
            "predicao": self.model.predict(X_scaled)
        })

        if tem_rotulos:
            y_real = df["time"]
            desempenho = mean_squared_error(y_real, preds["predicao"])
        else:
            desempenho = None

        return preds, desempenho
