import streamlit as st
import pandas as pd
import plotly.express as px
import pytz
from datetime import datetime
import json
import gdown
from streamlit_plotly_mapbox_events import plotly_mapbox_events

st.set_page_config(page_title = "Pycycle", layout="wide", initial_sidebar_state="collapsed")

header = st.container()
app = st.container()
dataviz = st.container()

@st.cache()
def load_data(url):
    url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
    df = pd.read_csv(url)

    return df


token = "pk.eyJ1IjoiY2FtaWxpYWIiLCJhIjoiY2w3a284am1uMDg5ejNvdDV6cWNzdTFsaSJ9.7nOYlVU0P_oLhl-7BnIu6Q"
affluence_compteur = load_data("https://drive.google.com/file/d/1-C2wCqL-A0Z07oxqoVSjKk3QZYG8wwcF/view?usp=sharing")

affluence_heure = load_data("https://drive.google.com/file/d/1aFA3dbK4VSK2h79UIgM9yTXzpO9gzf2h/view?usp=sharing")
affluence_heure = affluence_heure.reset_index(drop=False)
affluence_heure['Heure'] = affluence_heure['Heure'].astype(str)


with header:
    st.header("Pycycle - Prédiction du trafic cycliste à Paris")
    st.caption("Camilia Bouda, Gilles Schenfele")
    st.markdown("#### :bicyclist:  Découvrez l'état du trafic cycliste aujourd'hui !")
    st.write('')
    st.info("Sélectionner un jour de la semaine et un compteur sur la carte pour voir son affluence habituelle au fil de la journée   ⬇️")
    if 'selected_bike_meter' not in st.session_state:
        st.session_state.selected_bike_meter = '[]'    

with app:
    tz = pytz.timezone('Europe/Paris')
    hour = datetime.now(tz).hour
    day_index = int(datetime.now(tz).strftime("%u")) - 1
        
    st.radio(label= 'Jour de la semaine', options=('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
            index=day_index, key='day', horizontal = True)
    
    filtered_df = affluence_compteur[affluence_compteur['Jour Type'] == st.session_state.day]
    filtered_df = filtered_df.rename(columns={'Comptage horaire': 'Comptage horaire moyen'})
    filtered_df = filtered_df.reset_index(drop=False)


    col1, col2 = st.columns((2, 1.5), gap="small")

    with col1:
        fig = px.scatter_mapbox(filtered_df, 
                                lat="Lat",
                                lon="Long", 
                                size="Comptage horaire moyen", 
                                color = "Comptage horaire moyen",
                                hover_name = "Nom du compteur",
                                hover_data = ['Jour Type'],
                                size_max=30,
                                zoom=10.5,
                                title="Affluence horaire habituelle")

        fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_layout(height = 400)

        mapbox_events = plotly_mapbox_events(
                                            fig,
                                            click_event=True,
                                            select_event=False,
                                            hover_event=False,
                                            relayout_event=False,
                                            override_width = "100%",
                                            key = 'selected_bike_meter')


    with col2:
        if st.session_state.selected_bike_meter != "[]":  #If a bike meter has been selected, we show the graph of the hourly trafic
            selected_bike_meter_index = json.loads(st.session_state.selected_bike_meter)[0][0]['pointIndex']
            selected_compteur_name = filtered_df.loc[selected_bike_meter_index, 'Nom du compteur']
            filtered_df2 = affluence_heure[(affluence_heure['Nom du compteur'] == selected_compteur_name) &(affluence_heure['Jour Type'] == st.session_state.day)]


            def color_map(now):
                color_map = {}
                for heure in range(24):
                    if heure == now:
                        color_map[str(heure)] = "#93129f"
                    else:
                        color_map[str(heure)] = '#e9d0ec'
                return color_map

            color_map = color_map(hour)

            fig2 = px.bar(filtered_df2, x="Heure", y="Comptage horaire", hover_data=['Nom du compteur', 'Affluence', 'Jour Type'],
                        color = "Heure", color_discrete_map=color_map)


            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig2.update_xaxes(ticksuffix="h")
            fig2.update_layout( height = 350,
                                showlegend=False, 
                                xaxis={'title': '','visible': True, 'showticklabels': True},
                                yaxis={"visible": False})

            affluence = str(filtered_df2.loc[affluence_heure['Heure'] == str(hour)]['Affluence']).split('\n')[0].split('  ')[-1]
            texte = "🕑 " + str(hour) + 'h: Habituellement **' + affluence.lower() + "**"

            st.markdown("📍 " + selected_compteur_name)
            st.markdown(texte)

            st.plotly_chart(fig2, use_container_width=True, config = {'displayModeBar': False})


with dataviz:
    st.markdown("#### :rocket: Explorer les données !")

with st.sidebar:
    st.caption("Pycycle - Prédiction du trafic cycliste à Paris \n Auteurs: Camilia Bouda, Gilles Schenfele")






