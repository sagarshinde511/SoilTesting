import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ---------------- Load Dataset and Train Model ----------------
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

# ---------------- Authentication System ----------------
def check_login(username, password):
    return username == "admin" and password == "adcet"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "logout_clicked" not in st.session_state:
    st.session_state.logout_clicked = False

# ---------------- Login Page ----------------
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")
    st.stop()

# ---------------- Logout Button ----------------
st.sidebar.title("👤 User Panel")
st.sidebar.success("Logged in as: admin")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.logout_clicked = True
    st.rerun()

# ---------------- Crop Prediction Interface ----------------
st.title("🌾 Crop Recommendation System")

tab1, = st.tabs(["Crop Prediction"])

with tab1:
    st.subheader("🔍 Input Soil and Weather Details")
    
    n = st.slider("Nitrogen (N)", 0, 150, 50)
    p = st.slider("Phosphorus (P)", 0, 150, 50)
    k = st.slider("Potassium (K)", 0, 150, 50)
    temperature = st.slider("Temperature (°C)", 0.0, 50.0, 25.0)
    humidity = st.slider("Humidity (%)", 0.0, 100.0, 50.0)
    ph = st.slider("pH", 0.0, 14.0, 6.5)
    rainfall = st.slider("Rainfall (mm)", 0.0, 300.0, 100.0)

    if st.button("Predict Best Crop"):
        input_data = [[n, p, k, temperature, humidity, ph, rainfall]]
        prediction = model.predict(input_data)[0]
        st.success(f"✅ Recommended Crop: **{prediction.upper()}**")
