import streamlit as st
import pandas as pd
import plotly.express as px
import pytz
from datetime import datetime
import gdown
from streamlit_plotly_mapbox_events import plotly_mapbox_events

st.set_page_config(page_title = "Pycycle", layout="wide")

header = st.container()
app = st.container()
dataviz = st.container()

with header:
    st.title("Pycycle")
    st.caption("Camilia Bouda, Gilles Schenfele")
    st.markdown("#### Découvrez l'état du trafic cycliste aujourd'hui ! :bicyclist:")
    st.write("Sélectionner un compteur sur la carte pour voir son affluence habituelle au fil de la journée ⬇️")

with app:
 
    @st.cache()
    def load_data(url):
        url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
        df = pd.read_csv(url)

        return df
    
    token = "pk.eyJ1IjoiY2FtaWxpYWIiLCJhIjoiY2w3a284am1uMDg5ejNvdDV6cWNzdTFsaSJ9.7nOYlVU0P_oLhl-7BnIu6Q"
    affluence_compteur = load_data("https://drive.google.com/file/d/1-C2wCqL-A0Z07oxqoVSjKk3QZYG8wwcF/view?usp=sharing")
    affluence_compteur = affluence_compteur.rename(columns={'Comptage horaire': 'Comptage horaire moyen'})
    affluence_compteur = affluence_compteur.reset_index(drop=False)

    fig = px.scatter_mapbox(affluence_compteur, 
                            lat="Lat",
                            lon="Long", 
                            size="Comptage horaire moyen", 
                            color = "Comptage horaire moyen",
                            hover_name = "Nom du compteur",
                            hover_data=["index"],
                            size_max=30,
                            zoom=10.5,
                            title="Affluence horaire habituelle",
                            )

    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(height = 400)

    plot_name_holder_clicked = st.empty()

    mapbox_events = plotly_mapbox_events(
        fig,
        click_event=True,
        select_event=False,
        hover_event=False,
        relayout_event=False,
        override_width = "100%")

    compteurs = affluence_compteur[['index', 'Nom du compteur']]
    selected_compteur_index = mapbox_events[0][0]['pointIndex']
    selected_compteur_name = affluence_compteur.loc[selected_compteur_index, 'Nom du compteur']

    

    affluence_heure = load_data("https://drive.google.com/file/d/1aFA3dbK4VSK2h79UIgM9yTXzpO9gzf2h/view?usp=sharing")
    affluence_heure = affluence_heure.reset_index(drop=False)

    df2 = affluence_heure[affluence_heure['Nom du compteur'] == selected_compteur_name]
    fig2 = px.bar(df2, x="Heure", y="Comptage horaire", hover_data=['Nom du compteur', 'Affluence'])
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig2.update_xaxes(ticksuffix="h")
    fig2.update_layout(height = 300)

    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz).hour
    affluence = str(df2.loc[df2['Heure'] == 20]['Affluence']).split('\n')[0].split('  ')[-1]
    texte = str(now) + 'h: Habituellement **' + affluence.lower() + "**"

    st.markdown("Compteur: " + selected_compteur_name)
    st.markdown(texte)
    st.plotly_chart(fig2, use_container_width=True)



with dataviz:
    st.markdown("#### Explorer les données ! :rocket:")
    






