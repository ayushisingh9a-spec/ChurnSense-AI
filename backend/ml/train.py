import os
<<<<<<< HEAD
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
=======
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

# ==========================================================
# PROJECT DIRECTORY
# ==========================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

# ==========================================================
# DATASET PATH
# ==========================================================

excel_file = os.path.join(
    BASE_DIR,
    "dataset",
    "sample_churn_dataset.xlsx"
)

csv_file = os.path.join(
    BASE_DIR,
    "dataset",
    "sample_churn_dataset.csv"
)

# Load whichever dataset exists
if os.path.exists(excel_file):
    dataset_path = excel_file
    df = pd.read_excel(dataset_path)

elif os.path.exists(csv_file):
    dataset_path = csv_file
    df = pd.read_csv(dataset_path)

else:
    raise FileNotFoundError(
        "No dataset found inside dataset folder."
    )

# ==========================================================
# START
# ==========================================================

print("=" * 60)
print(" CUSTOMER CHURN PREDICTION MODEL ")
print("=" * 60)

print("\nDataset Loaded Successfully!")

print("\nDataset Location:")
print(dataset_path)

print("\nFirst Five Rows\n")
print(df.head())

print("\nDataset Shape :", df.shape)

# ==========================================================
# REMOVE CUSTOMER ID
# ==========================================================

if "customerID" in df.columns:
    df.drop(columns=["customerID"], inplace=True)

# ==========================================================
# ENCODE CATEGORICAL DATA
# ==========================================================

print("\nEncoding Categorical Columns...")

for col in df.columns:

    if not pd.api.types.is_numeric_dtype(df[col]):
        df[col] = pd.factorize(df[col].astype(str))[0]

print("Encoding Completed!")

print("\nData Types After Encoding\n")
print(df.dtypes)

# ==========================================================
# FEATURES & TARGET
# ==========================================================

X = df.drop("Churn", axis=1)

y = df["Churn"]

# Save feature names
feature_columns = X.columns.tolist()

# ==========================================================
# TRAIN TEST SPLIT
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining Records :", len(X_train))
print("Testing Records  :", len(X_test))

# ==========================================================
# MODEL
# ==========================================================

print("\nTraining Random Forest Model...")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

print("Model Training Completed!")

# ==========================================================
# PREDICTIONS
# ==========================================================

predictions = model.predict(X_test)

# ==========================================================
# EVALUATION
# ==========================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\n" + "=" * 60)
print(" MODEL EVALUATION ")
print("=" * 60)

print(f"\nAccuracy : {accuracy * 100:.2f}%")

print("\nClassification Report\n")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)

print("Confusion Matrix\n")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)

# ==========================================================
# SAVE MODEL
# ==========================================================

model_folder = os.path.join(
    BASE_DIR,
    "model"
)

os.makedirs(
    model_folder,
    exist_ok=True
)

# Save trained model
joblib.dump(
    model,
    os.path.join(
        model_folder,
        "churn_model.pkl"
    )
)

# Save feature list
joblib.dump(
    feature_columns,
    os.path.join(
        model_folder,
        "feature_columns.pkl"
    )
)

print("\nModel Saved Successfully!")

print("\nSaved Files")

print("✔ churn_model.pkl")

print("✔ feature_columns.pkl")

print("\nModel Folder:")

print(model_folder)

print("\nTraining Completed Successfully!")

print("=" * 60)
>>>>>>> 25fa3d2c570c6df5642b2877f7ddaaceeba2f85c
