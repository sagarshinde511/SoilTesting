import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load and cache the dataset
@st.cache_data
def load_data():
    return pd.read_csv("Crop_recommendation.csv")

# Load data
data = load_data()

# Prepare features and target
X = data.drop("label", axis=1)
y = data["label"]

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Streamlit UI
st.title("🌾 Crop Recommendation System")

# Input from user
n = st.slider("Nitrogen (N)", 0, 150, 50)
p = st.slider("Phosphorus (P)", 0, 150, 50)
k = st.slider("Potassium (K)", 0, 150, 50)
temperature = st.slider("Temperature (°C)", 0.0, 50.0, 25.0)
humidity = st.slider("Humidity (%)", 0.0, 100.0, 50.0)
ph = st.slider("pH", 0.0, 14.0, 6.5)
rainfall = st.slider("Rainfall (mm)", 0.0, 300.0, 100.0)

# Predict crop
if st.button("Predict Best Crop"):
    input_data = [[n, p, k, temperature, humidity, ph, rainfall]]
    prediction = model.predict(input_data)[0]
    st.success(f"✅ Recommended Crop: **{prediction.upper()}**")
