import os

import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

df = pd.read_csv(os.path.join(BASE_DIR, 'data/Crop_recommendation.csv'))

X = df.drop('label', axis=1)
y = df['label']

le = LabelEncoder()
y_encoded = le.fit_transform(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier()
model.fit(X_scaled, y_encoded)

dump(model, os.path.join(BASE_DIR, 'models/model.pkl'))
dump(scaler, os.path.join(BASE_DIR, 'models/scaler.pkl'))
dump(le, os.path.join(BASE_DIR, 'models/label_encoder.pkl'))

print("✅ Model trained successfully (No warnings)")