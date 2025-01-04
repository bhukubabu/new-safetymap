import pandas as pd
import chardet
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
import streamlit as st
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from matplotlib import pyplot as plt

st.title("Check safety status on the map 🗺️")
with open("final_lat.csv", "rb") as f:
    encoding = chardet.detect(f.read())["encoding"]
df = pd.read_csv("final_lat.csv", encoding=encoding)

city_list = df[df['states'] == 'West bengal']['PLACE'].unique()

def create_dataframe(loca):
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')  # Convert to float, invalid values become NaN
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['intse'] = pd.to_numeric(df['intse'], errors='coerce')
    df.dropna(subset=['latitude', 'longitude', 'intse'], inplace=True)
    lat = df[df['PLACE'] == loca]['latitude'].unique()[0]
    lng = df[df['PLACE'] == loca]['longitude'].unique()[0]
    cluster = df[df['PLACE'] == loca]['cluster'].unique()[0]
    level = df[df['PLACE'] == loca]['level'].unique()[0]
    map_center = [lat, lng]
    coords = df[['latitude', 'longitude','intse']]

    # Initialize map centered on the selected location
    crime_map = folium.Map(location=map_center, zoom_start=8, control_scale=True)

    # Add a marker for the center location with crime level information
    folium.Marker(
        location=map_center,
        popup=f"Crime Zone Level: {level}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(crime_map)
    gradient = {
        0.2: 'blue',   # low intensity
        0.4: 'cyan',   
        0.6: 'lime',   
        0.8: 'orange',
        1.0: 'red'     # high intensity
    }
    # heatmap to the map based on latitude, longitude, and intensity
    HeatMap(data=coords[['latitude', 'longitude',"intse"]].values, blur=20, radius=8,gradient=gradient,blurr=1).add_to(crime_map)
    #crime_map.save("crime_map.html")
    return crime_map,level

def user_loc(loca, map_html):
    """Display the map in Streamlit."""
    with st.expander(f"Showing results for {loca}",expanded=True):
        components.html(map_html, height=500, width=550)

def display_crime_chart(loca):
    """Display a bar chart of crime types for the selected location."""
    location_data = df[df['PLACE'] == loca]

    # Group by crime type and count occurrences
    crime_counts = location_data['MURDER'].value_counts()
    crime_counts2 = location_data['DOWRY DEATHS'].value_counts()
    # Plotting the bar chart
    fig, ax = plt.subplots()
    crime_counts.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title(f'Murder in {loca}')
    ax.set_xlabel('Crime Type')
    ax.set_ylabel('Count')
    st.pyplot(fig)
    crime_counts2.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title(f'DOWRY DEATHS in {loca}')
    ax.set_xlabel('Crime Type')
    ax.set_ylabel('Count')
    st.pyplot(fig)
city_list = [" "] + list(city_list)
option = st.selectbox("Select city", city_list)

if option and option != " ":
    crime_map,level = create_dataframe(option)
    crime_map.save("crime_map.html")
    with open("crime_map.html", "r") as f:
        map_html = f.read()
    user_loc(option, map_html)
    if level=="low":
        st.success("You are in safe zone")
    else:
        st.warning("Its a medium crime zone")
    st.markdown("If you want more information about the location you can ask our chat bot or get the recent news about the place from our news bot. Hre are few plots for your convinence....")
    display_crime_chart(option)
else:
    st.write("Please select a location.")

print("Map has been saved as crime_clusters_map.html")
