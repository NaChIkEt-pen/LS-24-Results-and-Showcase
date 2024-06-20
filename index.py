import folium
import json
import streamlit as st
from streamlit_folium import st_folium
import os
import mysql.connector
import pandas as pd


st.set_page_config(layout="wide")
with open('styles.css') as f:
    st.markdown(f"<style>{f.read()} </style> ", unsafe_allow_html=True)
try:
    ###################### MYSQL CONNECTION ####################
    try:
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="nachiket",
          database="LS2024"
        )
    except:
        st.title("Database Connection Problem please Visit Later Thank You!")
    
    mycursor = mydb.cursor()
    mycursor.execute('SHOW COLUMNS FROM `maharashtra`;')
    columns = mycursor.fetchall()
    column_names = [i[0] for i in mycursor.description]
    df_cols = pd.DataFrame(columns, columns=column_names)
    ls_column_names = df_cols['Field'].tolist()

    
    mycursor.execute('SHOW TABLES;')
    names = mycursor.fetchall()
    table_names = [i[0] for i in mycursor.description]
    df_tables = pd.DataFrame(names)
    df_state_names = df_tables[0].tolist()
    # print("ls_column_names",ls_column_names)


    ###########################
    
    # file_contents = f.read()
    # styles = f.read()
    st.title("Lok Sabha 2024 Elections")
    st.text("Project showcases the general data and stats of the election in an interactive way.")
    
    
    col1, col2 = st.columns([1, 1],gap="large")
    
    ######### Map ###############
    with col1:
        st.subheader("Current Indian political landscape")
        # Define the path to your local GeoJSON file
        geojson_file_path = 'india_pc_2024_simplified.geojson'
    
        # Read the GeoJSON data from the file with specified encoding
        with open(geojson_file_path, 'r', encoding='utf-8') as geojson_file:
            geojson_data = json.load(geojson_file)
    
        # Create a map object centered at a particular latitude and longitude
        # Adjust the location and zoom level as needed
        m = folium.Map(location=[22.5, 85.0882],
                zoom_start=4.4,
                tiles='',
                attr="India only"
                )
    
        # style_function = lambda x: {'fillColor': '#ffffff', 
        #                             'color':'#000000', 
        #                             'fillOpacity': 0.1, 
        #                             'weight': 0.1}
    
        # Add the GeoJSON layer to the map  #########  , style_function=style_function
        g = folium.GeoJson(geojson_data, name="geojson",style_function=lambda feature: {
            "fillColor": "#000000",
            "color": "black ",
            "weight": 2,
            "dashArray": "5, 5",
        }, ).add_to(m)
        m.add_child(folium.LatLngPopup())
    
        # # Add layer control to toggle GeoJSON visibility
        # folium.LayerControl().add_to(m)
    
        # Save the map to an HTML file
        # m.save('map_with_geojson.html')
    
        folium.GeoJsonTooltip(fields=["pc_name"]).add_to(g)
        st_data  = st_folium(m,width=570, height=460,  key="map1")
        # If using Jupyter Notebook, display the map inline
        # m
        def get_pos(lat, lng):
            return lat, lng
    
        if st_data is not None and 'last_clicked' in st_data and st_data['last_clicked'] is not None:
            lat_long_data = get_pos(st_data['last_clicked']['lat'], st_data['last_clicked']['lng'])
            # print("st_data:",st_data)
            # print("lat, long: "lat_long_data)
        else:
            st.caption("Click on the map to get details of the Parliamentary Constituency.")
    
    
    with col2:
        st.subheader("State / Constituency wise data")
        col3, col4 = st.columns([1, 1],gap="large")
        with col3:
            if df_state_names != None:
                option_state = st.selectbox(
                "Select State",
                df_state_names)
        
        
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM `{option_state}`;")
        state_data = mycursor.fetchall()
        df_state_data = pd.DataFrame(state_data)
        print(ls_column_names)

        df_state_data.columns = ls_column_names

        ls_pc_name = df_state_data["Constituency"].tolist()
        ls_pc_name.sort()
        # print(ls_pc_name)
        with col4: 
            if ls_pc_name != None:
                option_pc = st.selectbox(
                    "Select Counstituency",
                    ls_pc_name
                )
        
        st.dataframe(df_state_data.loc[df_state_data["Constituency"] == option_pc], hide_index  = True) 
        st.markdown(""" <p id = "pc_caption">Double Click on the field to Expand.</p> """,  unsafe_allow_html=True)
        # st.caption("Double Click on the field to Expand.")

        m2 = folium.Map(location=[22.5, 85.0882],
                zoom_start=3,
                tiles='',
                attr="India only"
                )
    
        # style_function = lambda x: {'fillColor': '#ffffff', 
        #                             'color':'#000000', 
        #                             'fillOpacity': 0.1, 
        #                             'weight': 0.1}
    
        # Add the GeoJSON layer to the map  #########  , style_function=style_function
        g2 = folium.GeoJson(geojson_data, name="geojson2",style_function=lambda feature: {
            "fillColor": "#000000",
            "color": "black ",
            "weight": 2,
            "dashArray": "5, 5",
        }).add_to(m2)
        m2.add_child(folium.LatLngPopup())
    
        # # Add layer control to toggle GeoJSON visibility
        # folium.LayerControl().add_to(m)
    
        # Save the map to an HTML file
        # m.save('map_with_geojson.html')
    
        folium.GeoJsonTooltip(fields=["pc_name"]).add_to(g2)
        st_data2  = st_folium(m2,width=200, height=240,  key="map2")
except Exception as Argument:
    st.title("Some Unexpected Error Occured")
    print(Argument)



