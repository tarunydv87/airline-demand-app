import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("AVIATIONSTACK_API_KEY")

st.title("✈️ Airline Market Demand Dashboard")

@st.cache_data
def fetch_data():
    if not api_key:
        raise ValueError("API key not found. Please set it in the .env file as AVIATIONSTACK_API_KEY.")

    url = f"http://api.aviationstack.com/v1/flights?access_key={api_key}&limit=100"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise ValueError("Failed to fetch data from AviationStack API. Please check your API key or request limits.")
    
    data = response.json()
    
    if 'data' not in data:
        raise ValueError("Unexpected response format from API.")
    
    df = pd.json_normalize(data['data'])
    return df

# Load and display data
try:
    df = fetch_data()
    st.success("✅ Flight data loaded successfully!")
    
    st.subheader("🌍 Popular Routes")
    routes = df.groupby(['departure.iata', 'arrival.iata']).size().reset_index(name='count')
    top_routes = routes.sort_values(by='count', ascending=False).head(10)
    fig = px.bar(top_routes, x='count', y='arrival.iata', color='departure.iata', orientation='h')
    st.plotly_chart(fig)

    st.subheader("📅 Flight Volume by Date")
    df['date'] = pd.to_datetime(df['departure.scheduled'], errors='coerce').dt.date
    daily_flights = df.groupby('date').size().reset_index(name='flights')
    fig2 = px.line(daily_flights, x='date', y='flights')
    st.plotly_chart(fig2)

except Exception as e:
    st.error(f"❌ Error: {e}")
