import folium
import json
import streamlit as st
from streamlit_folium import st_folium
import os
import mysql.connector
import pandas as pd
import sqlite3

# Streamlit configuration
st.set_page_config(layout="wide")

# Load CSS file
with open('styles.css') as f:
    st.markdown(f"<style>{f.read()} </style> ", unsafe_allow_html=True)

def create_sqlite_db():
    # Create a new SQLite database or connect to an existing one
    conn = sqlite3.connect('ls2024.db')
    return conn

def save_data_to_sqlite(df, table_name):
    conn = create_sqlite_db()
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def fetch_data_from_sqlite(table_name):
    conn = create_sqlite_db()
    df = pd.read_sql(f'SELECT * FROM `{table_name}`', conn)
    conn.close()
    return df

# Fetch data from MySQL and save it to SQLite
def fetch_data_from_mysql():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="nachiket",
            database="LS2024"
        )
    except mysql.connector.Error as err:
        return None

    mycursor = mydb.cursor()
    mycursor.execute('SHOW TABLES;')
    table_names = [table[0] for table in mycursor.fetchall()]

    for table_name in table_names:
        mycursor.execute(f'SELECT * FROM `{table_name}`;')
        data = mycursor.fetchall()
        columns = [col[0] for col in mycursor.description]
        df = pd.DataFrame(data, columns=columns)
        save_data_to_sqlite(df, table_name)
    
    return table_names

# Load GeoJSON data
def load_geojson(path):
    geojson_file_path = path
    with open(geojson_file_path, 'r', encoding='utf-8') as geojson_file:
        geojson_data = json.load(geojson_file)
    return geojson_data

# Main code
try:
    table_names = fetch_data_from_mysql()
    if table_names is None:
        conn = create_sqlite_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        table_names = [table[0] for table in cursor.fetchall()]
        conn.close()

    if not table_names:
        st.title("Database Connection Problem please Visit Later Thank You!")
    else:
        ###################### MYSQL CONNECTION ####################
        mycursor = None
        if mycursor:
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
        else:
            df_state_names = table_names

        ###########################

        # file_contents = f.read()
        # styles = f.read()
        # st.title("Still Working on the Dashboard")
        st.title("Lok Sabha 2024 Elections")
        st.text("Project showcases the general data and stats of the election in an interactive way.")

        col1, col2 = st.columns([1, 1], gap="large")

        ######### Map ###############
        with col1:
            st.subheader("Current Indian political landscape")
            # Define the path to your local GeoJSON file
            geojson_file_path = 'india_pc_2024_simplified.geojson'

            # Read the GeoJSON data from the file with specified encoding
            geojson_data = load_geojson('india_pc_2024_simplified.geojson')

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
            g = folium.GeoJson(geojson_data, name="geojson", style_function=lambda feature: {
                "fillColor": "#000000",
                "color": "black ",
                "weight": 2,
                "dashArray": "5, 5",
            }).add_to(m)
            m.add_child(folium.LatLngPopup())

            # # Add layer control to toggle GeoJSON visibility
            # folium.LayerControl().add_to(m)

            # Save the map to an HTML file
            # m.save('map_with_geojson.html')

            folium.GeoJsonTooltip(fields=["pc_name"]).add_to(g)
            st_data = st_folium(m, width=570, height=460, key="map1")
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
            col3, col4 = st.columns([1, 1], gap="large")
            with col3:
                if df_state_names:
                    option_state = st.selectbox(
                        "Select State",
                        df_state_names)

            if mycursor:
                mycursor.execute(f"SELECT * FROM `{option_state}`;")
                state_data = mycursor.fetchall()
                df_state_data = pd.DataFrame(state_data)
                df_state_data.columns = ls_column_names
            else:
                df_state_data = fetch_data_from_sqlite(option_state)

            ls_pc_name = df_state_data["Constituency"].tolist()
            ls_pc_name.sort()
            with col4:
                if ls_pc_name:
                    option_pc = st.selectbox(
                        "Select Counstituency",
                        ls_pc_name
                    )

            st.dataframe(df_state_data.loc[df_state_data["Constituency"] == option_pc], hide_index=True)
            st.markdown(""" <p id="pc_caption">Double Click on the field to Expand.</p> """, unsafe_allow_html=True)
            # st.caption("Double Click on the field to Expand.")

            df_state_cords = pd.read_csv('state_cords.csv',  encoding='ISO-8859-1')
            # st.dataframe(df_state_cords)


            for index, row in df_state_cords.iterrows():
                if (row["Name"].replace(" ", "").lower() == option_state.replace(" ","").lower()):
                    # print(row["Name"].replace(" ", "").lower() == option_state.replace(" ","").lower())
                    small_state_x = row["Latitude"]
                    small_state_y = row["Longitude"]
                    # print(small_state_x, small_state_y)
            ################### map ##############
            col5, col6 = st.columns([1, 1], gap="small")
            with col5:
                st.subheader("State Map")
                geojson_data2 = load_geojson('india_pc_2024_simplified.geojson')

                # for data in geojson_data2["features"]:
                #     if data["properties"]["st_name"] == "ANDAMAN & NICOBAR":
                #         print(data["properties"]["st_name"])
                m2 = folium.Map(location=[small_state_x, small_state_y],
                                zoom_start=5,
                                tiles='',
                                attr="India only"
                                )
                def style_functions(feature):
                    if feature["properties"]["st_name"].replace(" ", "").lower() not in  option_state.replace(" ","").lower():
                        return ({
                                    "fillColor": "#DDDDDD",
                                    "color": "black ",
                                    "weight": 0,
                                    "dashArray": "5, 5",
                                    }
                            )
                    if feature["properties"]["pc_name"].replace(" ", "").lower()  in option_pc.replace(" ","").lower() and option_pc!="" and feature["properties"]["pc_name"].replace(" ", "").lower() != "": 
                        return ({
                                    "fillColor": "red",
                                    "color": "black",
                                    "weight": 1,
                                    "dashArray": "5, 5",
                                    }
                            )
                    else:
                        return ({
                                    "fillColor": "white",
                                    "color": "black ",
                                    "weight": 1,
                                    "dashArray": "5, 5",
                                    }
                        )
                
                g2 = folium.GeoJson(geojson_data2, name="geojson2", style_function = style_functions).add_to(m2)

                folium.GeoJsonTooltip(fields=["pc_name"]).add_to(g2)
                st_data2 = st_folium(m2, width=200, height=240, key="map2")
                st.markdown(""" <p id="pc_caption">Constituency in red is the selected Constituency.</p> """, unsafe_allow_html=True)
            with col6:
                st.subheader("2019 Stats")
                df_2019_data = pd.read_csv('2019_Results_Winning_Candidate.csv',  encoding='ISO-8859-1')
                for data in (df_2019_data["Constituency"].tolist()):
                    if data.replace(" ","").lower() in option_pc.replace(" ","").lower():
                        st.dataframe(df_2019_data.loc[df_2019_data["Constituency"] == data].T.reset_index(), hide_index=True)
                        
except Exception as Argument:
    st.title("Some Unexpected Error Occured")
    print(Argument)
