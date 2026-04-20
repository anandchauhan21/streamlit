
import streamlit as st
import requests

# Your OpenWeatherMap API key
# You can get one from https://openweathermap.org/api
API_KEY = "YOUR_API_KEY" 
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

st.title("Weather Report App")

city = st.text_input("Enter city name:")

if st.button("Get Weather"):
    if city:
        try:
            params = {
                'q': city,
                'appid': API_KEY,
                'units': 'metric'  # or 'imperial' for Fahrenheit
            }
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            weather_data = response.json()

            if weather_data["cod"] == 200:
                main_data = weather_data["main"]
                weather_info = weather_data["weather"][0]

                st.subheader(f"Weather in {city}")
                st.write(f"Temperature: {main_data['temp']}°C")
                st.write(f"Feels like: {main_data['feels_like']}°C")
                st.write(f"Description: {weather_info['description'].capitalize()}")
                st.write(f"Humidity: {main_data['humidity']}%")
                st.write(f"Pressure: {main_data['pressure']} hPa")

            else:
                st.error(f"Error: {weather_data['message']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not retrieve weather data. Please check your internet connection or API key: {e}")
        except KeyError:
            st.error("City not found. Please enter a valid city name.")
    else:
        st.warning("Please enter a city name.")

