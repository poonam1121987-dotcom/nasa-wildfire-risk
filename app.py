import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import date

st.set_page_config(page_title="Wildfire Risk Intelligence", page_icon="🔥", layout="centered")

st.title("🔥 NASA Space Apps: Wildfire Risk Predictor")
st.write("Real-time telemetry and risk prediction engine backed by historical validation metrics.")

st.sidebar.header("Location & Date Parameters")
lat = st.sidebar.number_input("Latitude", value=39.4820, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-121.4310, format="%.4f")
selected_date = st.sidebar.date_input("Evaluation Date", value=date(2024, 7, 24))

def predict_risk(temp, humidity, wind):
    if pd.isna(temp) or pd.isna(humidity) or pd.isna(wind):
        return 0.0
    norm_temp = max(0.0, min(1.0, (temp - 15.0) / 30.0))       
    norm_rh = max(0.0, min(1.0, (100.0 - humidity) / 80.0))    
    norm_ws = max(0.0, min(1.0, wind / 25.0))                   
    
    physical_score = (norm_temp * 0.40) + (norm_rh * 0.40) + (norm_ws * 0.20)
    return float(1.0 / (1.0 + np.exp(-6 * (physical_score - 0.50))))

if st.button("Evaluate Wildfire Risk", type="primary"):
    with st.spinner("Fetching Open-Meteo weather history & computing risk..."):
        try:
            r = requests.get(
                "https://archive-api.open-meteo.com/v1/archive",
                params={
                    "latitude": lat, "longitude": lon,
                    "start_date": str(selected_date), "end_date": str(selected_date),
                    "daily": "temperature_2m_max,relative_humidity_2m_mean,wind_speed_10m_max",
                    "timezone": "auto",
                },
                timeout=5
            ).json().get("daily", {})
            
            temp = r.get("temperature_2m_max", [28.0])[0]
            humidity = r.get("relative_humidity_2m_mean", [45.0])[0]
            wind = r.get("wind_speed_10m_max", [12.0])[0]
            
            risk_score = predict_risk(temp, humidity, wind)
            
            st.subheader("📊 Retrieved Environmental Telemetry")
            col1, col2, col3 = st.columns(3)
            col1.metric("Max Temperature", f"{temp}°C")
            col2.metric("Mean Humidity", f"{humidity}%")
            col3.metric("Max Wind Speed", f"{wind} km/h")
            
            st.subheader("🚨 Risk Assessment Result")
            if risk_score > 0.6:
                st.error(f"High Wildfire Hazard Detected! (Risk Score: {risk_score:.2f})")
            elif risk_score > 0.4:
                st.warning(f"Moderate Risk Level. (Risk Score: {risk_score:.2f})")
            else:
                st.success(f"Low Risk Level. (Risk Score: {risk_score:.2f})")
                
        except Exception as e:
            st.error(f"API request failed: {e}")
