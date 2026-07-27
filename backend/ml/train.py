import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier

from backend.ml.preprocess import Preprocessor


class UniversalTrainer:

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.model = RandomForestClassifier(
            n_estimators=300,
            random_state=42
        )

    def load_dataset(self, path):
        if path.endswith(".csv"):
            return pd.read_csv(path)
        elif path.endswith(".xlsx"):
            return pd.read_excel(path)
        else:
            raise Exception("Unsupported file format.")

    def prepare(self, df):
        df = self.preprocessor.remove_id_columns(df)
        target = self.preprocessor.detect_target(df)

        X = df.drop(columns=[target])
        y = df[target]

        self.feature_order = list(X.columns)
        self.default_values = {}
        for c in X.columns:
            if pd.api.types.is_numeric_dtype(X[c]):
                self.default_values[c]=float(X[c].median())
            else:
                m=X[c].mode()
                self.default_values[c]=m.iloc[0] if not m.empty else ""

        X = self.preprocessor.fit_transform(X)
        self.preprocessor.save()

        return X, y

    def split(self, X, y):
        return train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        predictions = self.model.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)

        print("\nAccuracy:", round(accuracy * 100, 2), "%")
        print("\nClassification Report\n")
        print(classification_report(y_test, predictions))
        print("\nConfusion Matrix\n")
        print(confusion_matrix(y_test, predictions))

        return accuracy

    def save_model(self):
        os.makedirs("model", exist_ok=True)

        joblib.dump(
            self.model,
            "model/churn_model.pkl"
        )

        metadata = {
            "feature_order": getattr(self,"feature_order",[]),
            "numeric_columns": getattr(self.preprocessor,"numeric_cols",[]),
            "categorical_columns": getattr(self.preprocessor,"categorical_cols",[]),
            "default_values": getattr(self,"default_values",{})
        }

        joblib.dump(
            metadata,
            "model/metadata.pkl"
        )

        print("\nModel Saved Successfully.")

    def run(self, dataset_path):
        print("\nLoading Dataset...")

        df = self.load_dataset(dataset_path)
        print("Rows:", len(df))

        X, y = self.prepare(df)

        X_train, X_test, y_train, y_test = self.split(X, y)

        print("\nTraining Model...")
        self.train(X_train, y_train)

        self.evaluate(X_test, y_test)
        self.save_model()

        print("\nTraining Completed.")


if __name__ == "__main__":
    trainer = UniversalTrainer()

    dataset_path = input("Enter dataset path: ").strip()

    trainer.run(dataset_path)
