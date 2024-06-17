import folium
import json
import streamlit as st
from streamlit_folium import st_folium

st.title("Lok Sabha 2024 Elections")
st.caption("Project showcases the general data and stats of the election in an interactive way.")

######### Map ###############
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

# style_function = lambda x: {'fillColor': '#ffffff', 
#                             'color':'#000000', 
#                             'fillOpacity': 0.1, 
#                             'weight': 0.1}

# Add the GeoJSON layer to the map  #########  , style_function=style_function
g = folium.GeoJson(geojson_data, name="geojson" ).add_to(m)
m.add_child(folium.LatLngPopup())

# # Add layer control to toggle GeoJSON visibility
# folium.LayerControl().add_to(m)

# Save the map to an HTML file
# m.save('map_with_geojson.html')

folium.GeoJsonTooltip(fields=["pc_name"],style="background-color: red;").add_to(g)
st_data  = st_folium(m, width=700)
# If using Jupyter Notebook, display the map inline
# m
def get_pos(lat, lng):
    return lat, lng

if st_data is not None and 'last_clicked' in st_data and st_data['last_clicked'] is not None:
    lat_long_data = get_pos(st_data['last_clicked']['lat'], st_data['last_clicked']['lng'])
    # print(st_data)
    print(lat_long_data)
else:
    st.subheader("Click on the map to get details of the Parliamentary Constituency.")
