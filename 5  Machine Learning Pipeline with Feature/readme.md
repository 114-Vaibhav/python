# Task 5: Machine Learning Pipeline with Feature Engineering

This task builds a customer churn prediction pipeline using the **Telco Customer Churn** dataset.  
The script performs data cleaning, feature engineering, encoding, outlier removal, scaling, model comparison, and model saving.

## What the program does

- Loads the dataset from `Telco-Customer-Churn.csv`
- Cleans the `TotalCharges` column and fills missing values with the median
- Removes the `customerID` column
- Creates new features:
  - `TenureGroup`
  - `TotalServices`
  - `AvgChargePerMonth`
  - `FamilyType`
- Encodes categorical values using label mapping and one-hot encoding
- Removes outliers from selected numerical columns using the IQR method
- Scales numerical features with `StandardScaler`
- Trains and evaluates these models:
  - Logistic Regression
  - Random Forest
  - SVM
  - XGBoost with `GridSearchCV`
- Compares models using Accuracy, Precision, Recall, and F1-score
- Saves the best model as `churn_model.pkl`

## Files

- `main.py` - main machine learning pipeline
- `Output.txt` - saved terminal output of the program
- `readme.md` - project explanation

## Requirements

Install the required libraries before running:

```bash
pip install pandas numpy scikit-learn xgboost joblib
```

## Run

```bash
python main.py
```

## Result

Based on the current output in `Output.txt`:

- Dataset loaded: `7043` records
- Features after encoding: `39`
- Best model: `Logistic Regression`
- Model file created: `churn_model.pkl`

This task shows a complete end-to-end machine learning workflow with basic feature engineering and model selection.
