import os
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