import folium
import json
import streamlit as st
from streamlit_folium import st_folium
import os



st.set_page_config(layout="wide")

stat = os.stat("styles.css")
last_modified_time = stat.st_mtime


with open('styles.css') as f:
    st.markdown(f"<style>{f.read()} </style> ", unsafe_allow_html=True)
    # file_contents = f.read()
    # styles = f.read()



if last_modified_time != os.path.getmtime("styles.css"):
    st.rerun()



st.title("Lok Sabha 2024 Elections")
st.caption("Project showcases the general data and stats of the election in an interactive way.")



col1, col2 = st.columns([1, 0.5],gap="large")

######### Map ###############
with col1:
    # Define the path to your local GeoJSON file
    geojson_file_path = 'india_pc_2019.geojson'

    # Read the GeoJSON data from the file with specified encoding
    with open(geojson_file_path, 'r', encoding='utf-8') as geojson_file:
        geojson_data = json.load(geojson_file)

    # Create a map object centered at a particular latitude and longitude
    # Adjust the location and zoom level as needed
    m = folium.Map(location=[22.5, 85.0882],
            zoom_start=4,
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
    st.markdown('<div id="map-container">', unsafe_allow_html=True)
    st_data  = st_folium(m,width=500, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
    # If using Jupyter Notebook, display the map inline
    # m
    def get_pos(lat, lng):
        return lat, lng

    if st_data is not None and 'last_clicked' in st_data and st_data['last_clicked'] is not None:
        lat_long_data = get_pos(st_data['last_clicked']['lat'], st_data['last_clicked']['lng'])
        # print(st_data)
        print(lat_long_data)
    else:
        st.caption("Click on the map to get details of the Parliamentary Constituency.")


with col2:
    st.subheader("State / Counstitunecy wise data")