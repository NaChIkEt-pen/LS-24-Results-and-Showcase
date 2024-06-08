import folium
import json
import streamlit as st
from streamlit_folium import st_folium
# Define the path to your local GeoJSON file
geojson_file_path = 'india_pc_2019.geojson'

# Read the GeoJSON data from the file with specified encoding
with open(geojson_file_path, 'r', encoding='utf-8') as geojson_file:
    geojson_data = json.load(geojson_file)

# Create a map object centered at a particular latitude and longitude
# Adjust the location and zoom level as needed
m = folium.Map(location=[23.5, 83.0882],
        zoom_start=4.5,
        tiles='',
        attr="India only"
        )

# Add the GeoJSON layer to the map
g = folium.GeoJson(geojson_data, name="geojson").add_to(m)

# # Add layer control to toggle GeoJSON visibility
folium.LayerControl().add_to(m)

# Save the map to an HTML file
# m.save('map_with_geojson.html')

folium.GeoJsonTooltip(fields=["pc_name"]).add_to(g)
st_data  = st_folium(m, width =700)

# If using Jupyter Notebook, display the map inline
# m