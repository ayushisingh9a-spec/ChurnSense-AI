import os
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder


class Preprocessor:

    def __init__(self):

        self.pipeline = None
        self.numeric_cols = None
        self.categorical_cols = None

    def remove_id_columns(self, df):

        remove_cols = []

        keywords = [
            "id",
            "customerid",
            "customer_id",
            "userid",
            "user_id",
            "accountnumber",
            "account_number"
        ]

        for col in df.columns:

            lower = col.lower()

            for word in keywords:

                if word in lower:

                    remove_cols.append(col)

                    break

        return df.drop(columns=remove_cols, errors="ignore")

    def detect_target(self, df):

        targets = [
            "Churn",
            "Exited",
            "Attrition",
            "Leave",
            "Target",
            "Status"
        ]

        for col in targets:

            if col in df.columns:

                return col

        raise Exception(
            "Target column not found."
        )

    def fit(self, X):

        self.numeric_cols = X.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()

        self.categorical_cols = X.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()

        numeric = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="median")
                )
            ]
        )

        categorical = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="most_frequent")
                ),
                (
                    "encoder",
                    OneHotEncoder(
                        handle_unknown="ignore"
                    )
                )
            ]
        )

        self.pipeline = ColumnTransformer(

            transformers=[

                (
                    "num",
                    numeric,
                    self.numeric_cols
                ),

                (
                    "cat",
                    categorical,
                    self.categorical_cols
                )

            ]

        )

        self.pipeline.fit(X)

        return self.pipeline

    def transform(self, X):

        return self.pipeline.transform(X)

    def fit_transform(self, X):

        self.fit(X)

        return self.transform(X)

    def save(self):

        os.makedirs("model", exist_ok=True)

        joblib.dump(
            self.pipeline,
            "model/preprocessor.pkl"
        )

    def load(self):

        self.pipeline = joblib.load(
            "model/preprocessor.pkl"
        )

        return self.pipeline