import streamlit as st
import pandas as pd
import mysql.connector
from sklearn.ensemble import RandomForestClassifier

# ---------------- Database Config ----------------
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

# ---------------- Load & Train Model ----------------
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

# ---------------- Fetch Latest DB Data ----------------
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

# ---------------- Login System ----------------
def check_login(username, password):
    return username == "admin" and password == "adcet"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()

# ---------------- Logout Button ----------------
st.sidebar.title("👤 User Panel")
st.sidebar.success("Logged in as: admin")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ---------------- Tabs ----------------
st.title("🌾 Crop Recommendation System")

tab1, tab2 = st.tabs(["Live Data", "Predict Crop"])

# ---------------- Tab 1: Fetch & Input ----------------

with tab1:
    st.subheader("🌱 Latest Environmental Data from MySQL")

    env_data = get_latest_soil_data()

    if env_data:
        st.session_state.env_data = env_data
        st.json(env_data)
    else:
        st.warning("⚠️ No environmental data found in the database.")

# -------- Tab 2: Prediction --------
with tab2:
    st.subheader("🧪 Enter Soil Nutrients")
    n = st.slider("Nitrogen (N)", 0, 150, 50)
    p = st.slider("Phosphorus (P)", 0, 150, 50)
    k = st.slider("Potassium (K)", 0, 150, 50)

    if "env_data" in st.session_state:
        env_data = st.session_state.env_data

        input_data = [[
            n, p, k,
            env_data["temperature"],
            env_data["humidity"],
            env_data["ph"],
            env_data["rainfall"]
        ]]

        if st.button("🔍 Predict Crop"):
            prediction = model.predict(input_data)[0]
            st.success(f"✅ Recommended Crop: **{prediction.upper()}**")
    else:
        st.warning("⚠️ Please visit 'Live Data' tab first to load environmental data.")

    if "user_input" in st.session_state:
        input_data = st.session_state.user_input
        st.write("📋 Using this data for prediction:", input_data)

        input_list = [[
            input_data["n"], input_data["p"], input_data["k"],
            input_data["temperature"], input_data["humidity"],
            input_data["ph"], input_data["rainfall"]
        ]]

        if st.button("Predict Crop"):
            prediction = model.predict(input_list)[0]
            st.success(f"✅ Recommended Crop: **{prediction.upper()}**")
    #else:
     #   st.warning("⚠️ Please fill inputs in 'Live Data' tab first.")

with tab3:
    st.subheader("🧪 Enter Current NPK Levels")
    fn = st.slider("Nitrogen (N)", 0, 150, 50)
    fp = st.slider("Phosphorus (P)", 0, 150, 50)
    fk = st.slider("Potassium (K)", 0, 150, 50)

    # Ideal NPK ranges (sample based on general crop average)
    IDEAL = {
        "N": 90,
        "P": 40,
        "K": 40
    }

    def fertilizer_advice(current, ideal, nutrient_name):
        diff = current - ideal
        if diff < -10:
            return f"🔼 Add more **{nutrient_name}** (deficiency of {abs(diff)} units)"
        elif diff > 10:
            return f"🔽 Reduce **{nutrient_name}** (excess of {abs(diff)} units)"
        else:
            return f"✅ **{nutrient_name}** level is optimal"

    if st.button("💡 Recommend Fertilizer Adjustment"):
        st.info("Based on general ideal NPK levels (N:90, P:40, K:40):")

        st.write(fertilizer_advice(fn, IDEAL["N"], "Nitrogen"))
        st.write(fertilizer_advice(fp, IDEAL["P"], "Phosphorus"))
        st.write(fertilizer_advice(fk, IDEAL["K"], "Potassium"))
