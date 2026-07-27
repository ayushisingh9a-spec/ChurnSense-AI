import joblib
import pandas as pd

from backend.ml.preprocess import Preprocessor


class UniversalPredictor:

    def __init__(self):

        self.model = joblib.load(
            "model/churn_model.pkl"
        )

        self.preprocessor = Preprocessor()

        self.preprocessor.load()

        self.metadata = joblib.load(
            "model/metadata.pkl"
        )

    def remove_id_columns(self, df):

        return self.preprocessor.remove_id_columns(df)

    def preprocess(self, df):

        df = self.remove_id_columns(df)
        feature_order=self.metadata.get("feature_order",[])
        defaults=self.metadata.get("default_values",{})
        if "TotalSpend" not in df.columns and {"MonthlyCharges","Tenure"}.issubset(df.columns):
            df["TotalSpend"]=df["MonthlyCharges"]*df["Tenure"]
        for c in feature_order:
            if c not in df.columns:
                df[c]=defaults.get(c,0)
        if feature_order:
            df=df[feature_order]
        return self.preprocessor.transform(df)

    def predict_dataframe(self, df):

        X = self.preprocess(df)

        predictions = self.model.predict(X)

        probabilities = self.model.predict_proba(X)

        churn_probability = []

        for p in probabilities:

            churn_probability.append(
                round(max(p) * 100, 2)
            )

        df["Prediction"] = predictions

        df["Probability"] = churn_probability

        return df

    def predict_single(self, customer_dict):

        df = pd.DataFrame([customer_dict])

        X = self.preprocess(df)

        prediction = self.model.predict(X)[0]

        probability = round(
            max(self.model.predict_proba(X)[0]) * 100,
            2
        )

        return {
            "Prediction": prediction,
            "Probability": probability
        }