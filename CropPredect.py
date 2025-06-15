import streamlit as st
import pandas as pd
import mysql.connector
from sklearn.ensemble import RandomForestClassifier

# --------- Database Credentials ---------
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

# --------- Load CSV & Train ML Model ---------
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

# --------- Get Latest Soil & Env Data from MySQL ---------
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

# --------- Simple Login Logic ---------
def check_login(username, password):
    return username == "admin" and password == "rit"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "logout" not in st.session_state:
    st.session_state.logout = False

# --------- Login Page ---------
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.stop()

# --------- Logout Button ---------
st.sidebar.title("👤 User Panel")
st.sidebar.success("Logged in as: admin")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

# --------- Crop Prediction Interface ---------
st.title("🌾 Crop Recommendation System (DB + User Input)")

tab1, = st.tabs(["Predict Crop"])

with tab1:
    env_data = get_latest_soil_data()

    if env_data:
        st.success("✅ Environmental data loaded from database:")
        st.write(env_data)

        st.subheader("🔢 Enter Soil Nutrients")
        n = st.slider("Nitrogen (N)", 0, 150, 50)
        p = st.slider("Phosphorus (P)", 0, 150, 50)
        k = st.slider("Potassium (K)", 0, 150, 50)

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
        st.error("❌ No environmental data found in the database.")
