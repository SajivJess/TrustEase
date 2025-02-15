# Importing necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
import xgboost as xgb

# Generating a synthetic dataset for demonstration purposes
# Features: Social media activity, utility payments, spending habits, health & fitness, phone/email longevity, insurance, job/location switches, entertainment payments, e-wallet transactions.
data = {
    'social_media_activity': np.random.randint(0, 2, 1000),  # 0 = low, 1 = high
    'utility_payments': np.random.randint(50, 300, 1000),  # Monthly payment in $ 
    'spending_habits': np.random.randint(100, 500, 1000),  # Monthly spending in $
    'health_fitness': np.random.randint(0, 2, 1000),  # 0 = low, 1 = high
    'phone_number_longevity': np.random.randint(1, 15, 1000),  # Years
    'email_longevity': np.random.randint(1, 20, 1000),  # Years
    'insurance_coverage': np.random.randint(0, 2, 1000),  # 0 = no, 1 = yes
    'job_switches': np.random.randint(0, 5, 1000),  # Number of job switches
    'location_switches': np.random.randint(0, 10, 1000),  # Number of times moved
    'entertainment_spending': np.random.randint(50, 200, 1000),  # Monthly entertainment spending
    'ewallet_transactions': np.random.randint(10, 1000, 1000)  # Monthly e-wallet transaction count
}

# Target: Credit Risk Classification (0 = Low Risk, 1 = High Risk)
# Simulating target: 0 (Low Risk) for higher credit score (600-850), 1 (High Risk) for lower credit score (300-599)
target = np.random.choice([0, 1], size=1000, p=[0.7, 0.3])  # 70% low risk, 30% high risk

# Creating a DataFrame
df = pd.DataFrame(data)
df['target'] = target

# Splitting the dataset into features (X) and target (y)
X = df.drop(columns=['target'])
y = df['target']

# Splitting data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scaling the features to standardize them
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Initializing and training the XGBoost model
model = xgb.XGBClassifier(eval_metric='logloss')
model.fit(X_train_scaled, y_train)

# Making predictions
y_pred = model.predict(X_test_scaled)

# Calculate the average credit score based on predicted risk category
credit_scores = []
for pred in y_pred:
    if pred == 0:  # Low risk (indicating a higher credit score)
        credit_scores.append(np.random.randint(600, 850))  # Low-risk borrowers have high credit score
    else:  # High risk (indicating a lower credit score)
        credit_scores.append(np.random.randint(300, 600))  # High-risk borrowers have low credit score

# Calculate the average score for the test set
avg_score = np.mean(credit_scores)

# Plot the pie chart to visualize the risk distribution
labels = ['Low Risk', 'High Risk']
sizes = [np.sum(y_pred == 0), np.sum(y_pred == 1)]
colors = ['#66b3ff','#ff9999']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title(f'Credit Score Risk Breakdown\nAverage Credit Score: {avg_score:.2f}')
plt.show()

# Output risk classification (Low or High) based on the predicted result
risk_classification = 'Low Risk' if avg_score >= 600 else 'High Risk'
print(f'The predicted borrower risk is: {risk_classification} with an average credit score of {avg_score:.2f}')

# Evaluate the model accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy of the XGBoost model: {accuracy * 100:.2f}%')

# Cross-validation to ensure the model is not overfitting
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
print(f'Cross-validation accuracy: {cv_scores.mean() * 100:.2f}%')