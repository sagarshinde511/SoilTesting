import streamlit as st
import pandas as pd
import mysql.connector
from sklearn.ensemble import RandomForestClassifier

# DB Credentials
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

# Load dataset & train model
@st.cache_data
def load_data():
    return pd.read_csv("Crop_recommendation.csv")

@st.cache_resource
def train_model():
    data = load_data()
    X = data.drop("label", axis=1)
    y = data["label"]
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    return model

model = train_model()

# Get latest environmental data from MySQL
def get_latest_soil_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM SoilData ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {
                "ph": float(row["SoilPH"]),
                "rainfall": float(row["SoilMoisture"]),
                "temperature": float(row["EnvarmentTemp"]),
                "humidity": float(row["EnvarmentHumi"])
            }
        else:
            return None
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

# ------------------- UI -------------------
st.title("🌾 Crop Prediction from Database + User Input")

# Step 1: Get environmental data
env_data = get_latest_soil_data()

if env_data:
    st.success("✅ Environmental data loaded from database (latest row):")
    st.write(env_data)

    # Step 2: Take N, P, K from user
    st.subheader("🔢 Enter Soil Nutrients")
    n = st.slider("Nitrogen (N)", 0, 150, 50)
    p = st.slider("Phosphorus (P)", 0, 150, 50)
    k = st.slider("Potassium (K)", 0, 150, 50)

    # Step 3: Predict
    if st.button("🔍 Predict Best Crop"):
        input_data = [[
            n, p, k,
            env_data["temperature"],
            env_data["humidity"],
            env_data["ph"],
            env_data["rainfall"]
        ]]
        prediction = model.predict(input_data)[0]
        st.success(f"✅ Recommended Crop: **{prediction.upper()}**")
else:
    st.error("❌ Could not retrieve environmental data from the database.")
