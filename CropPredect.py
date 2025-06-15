import streamlit as st
import pandas as pd
import mysql.connector
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Database config
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

def get_soil_data():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SoilData ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result

# Dummy models (replace with trained models later)
def predict_crop(n, p, k, temp, humidity, moisture, ph):
    # Dummy logic (replace with real ML model)
    if n > 100:
        return "Wheat"
    elif p > 50:
        return "Rice"
    else:
        return "Maize"

def recommend_fertilizer(n, p, k):
    # Dummy logic
    if n < 50:
        return "Urea"
    elif p < 30:
        return "DAP"
    elif k < 40:
        return "MOP"
    else:
        return "Balanced NPK"

# Streamlit UI
st.set_page_config(page_title="Crop & Fertilizer Prediction", layout="wide")
st.title("🌾 ML Based Crop and Fertilizer Prediction System")

tab1, tab2, tab3 = st.tabs(["🌱 Crop Prediction", "🌾 Fertilizer Suggestion", "📊 Data Analysis"])

with tab1:
    st.header("Enter NPK Values")
    n = st.number_input("Nitrogen (N)", min_value=0, max_value=500, value=50)
    p = st.number_input("Phosphorus (P)", min_value=0, max_value=500, value=40)
    k = st.number_input("Potassium (K)", min_value=0, max_value=500, value=30)

    soil = get_soil_data()
    if soil:
        st.success("Fetched latest soil data from database")
        st.write(soil)

        crop = predict_crop(n, p, k,
                            float(soil['EnvarmentTemp']),
                            float(soil['EnvarmentHumi']),
                            float(soil['SoilMoisture']),
                            float(soil['SoilPH']))
        st.subheader(f"✅ Recommended Crop: **{crop}**")
    else:
        st.error("No soil data found in database!")

with tab2:
    st.header("Fertilizer Suggestion Based on NPK")
    fertilizer = recommend_fertilizer(n, p, k)
    st.subheader(f"🌿 Recommended Fertilizer: **{fertilizer}**")

with tab3:
    st.header("Latest Soil Data")
    data = get_soil_data()
    if data:
        df = pd.DataFrame([data])
        st.dataframe(df)
        st.bar_chart(df.drop("id", axis=1))
    else:
        st.warning("No soil data available.")
