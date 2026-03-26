import pandas as pd 
import numpy as np
import time
import joblib
from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

print("\n---------------Data Preprocessing---------------\n")

df = pd.read_csv("Telco-Customer-Churn.csv")
print(f"Loaded {df.shape[0]:,} records ({df.shape[1]} features)")

print("\n---------------Data Cleaning---------------\n")

df['TotalCharges'] = pd.to_numeric(df["TotalCharges"],errors='coerce')

missing_tc = df["TotalCharges"].isnull().mean()*100
df["TotalCharges"].fillna(df["TotalCharges"].median(),inplace=True)

print(f"Missing Values filled: Total Charges ({missing_tc:.1f}%)")

df.drop("customerID",axis=1,inplace=True)

print("\n---------------Feature Engineering---------------\n    ")

def tenure_group(x):
    if(x <= 12): return '0-1yr'
    elif(x <= 24): return '1-2yr'
    elif(x <= 48): return '2-4yr'
    else: return '4+yr'

df["TenureGroup"] = df["tenure"].apply(tenure_group)

services =  ['PhoneService', 'MultipleLines', 'InternetService',
            'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
            'TechSupport', 'StreamingTV', 'StreamingMovies']

df['TotalServices'] = df[services].apply(lambda x: sum(x == 'Yes'), axis=1)
df['AvgChargePerMonth'] = df['TotalCharges'] / (df['tenure'] + 1)
df['FamilyType'] = df['Partner'] + "_" + df['Dependents']

print("Engineered 4 new features: TenureGroup, TotalServices, AvgChargePerMonth, FamilyType")

print("\n---------------Feature Encoding---------------\n    ")
binaryCols = ['Partner', 'Dependents', 'PhoneService',
               'PaperlessBilling', 'Churn']

for col in binaryCols:
    df[col] = df[col].map({'Yes': 1, 'No': 0 })

df['gender']= df['gender'].map({'Male':1, 'Female':0})

df = pd.get_dummies(df,drop_first=True);

print(f"After Encoding: {df.shape}")

print("\n----------------Outlier Removal----------\n")

def removeOutliers(df,cols):
    for col in cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower) & (df[col] <= upper)]
    return df

numCols = ['tenure', 'MonthlyCharges', 'TotalCharges', 'AvgChargePerMonth']
df = removeOutliers(df,numCols)

print(f"After Outlier Removal: {df.shape}")

print("\n---------------Scaling---------------\n")      

scaler = StandardScaler()
df[numCols] = scaler.fit_transform(df[numCols])

print(f"After Scaling: {df.shape}")

X = df.drop('Churn',axis=1)
y = df['Churn']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

print(f"Training Data: {X_train.shape}")
print(f"Testing Data: {X_test.shape}")

print('\n---------------Model Training---------------\n' )

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(),
    "SVM": SVC(),
}

results =[]
for name,model in models.items():
    scores = cross_validate(model, X, y, cv=5,
                            scoring=['accuracy', 'precision', 'recall', 'f1'])
    results.append([
        name,
        np.mean(scores['test_accuracy']),
        np.mean(scores['test_precision']),
        np.mean(scores['test_recall']),
        np.mean(scores['test_f1'])
    ])

xgb = XGBClassifier(eval_metric='logloss')

param_grid = {
    'max_depth': [4, 6],
    'learning_rate': [0.05, 0.1],
    'n_estimators': [200, 300]
}

grid = GridSearchCV(xgb, param_grid, cv=5, scoring='f1', verbose=0)
grid.fit(X_train, y_train)

best_xgb = grid.best_estimator_

scores = cross_validate(best_xgb, X, y, cv=5,
                        scoring=['accuracy', 'precision', 'recall', 'f1'])

results.append([
    "XGBoost (tuned)",
    np.mean(scores['test_accuracy']),
    np.mean(scores['test_precision']),
    np.mean(scores['test_recall']),
    np.mean(scores['test_f1'])
])
print("\n----------Model Evaluation----------\n")
print("+-------------------------+-----------+-----------+----------+--------+")
print("| Model                   | Accuracy  | Precision | Recall   | F1     |")
print("+-------------------------+-----------+-----------+----------+--------+")

for row in results:
    print(f"| {row[0]:<23} | {row[1]:.3f}     | {row[2]:.3f}     | {row[3]:.3f}   | {row[4]:.3f}  |")

print("+-------------------------+-----------+-----------+----------+--------+")

best_model_name = max(results, key=lambda x: x[4])[0]
print(f"\nBest Model: {best_model_name}")
bestModel = models[best_model_name]


if best_model_name == "XGBoost (tuned)":
    print("Hyperparameters:", grid.best_params_)
    final_model = best_xgb
else:
    final_model = models[best_model_name]


if hasattr(final_model, "feature_importances_"):
    importances = final_model.feature_importances_
    features = X.columns

    feat_imp = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)

    print("\nTop 5 Feature Importances:")
    for i in range(5):
        print(f"{i+1}. {feat_imp[i][0]} — {feat_imp[i][1]:.3f}")


joblib.dump(final_model, "churn_model.pkl")
print("\nModel saved to churn_model.pkl")