import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title = "Pycycle")

header = st.container()
app = st.container()
dataviz = st.container()

with header:
    st.title("Pycycle")
    st.caption("Camilia Bouda, Gilles Schenfele")
    st.markdown("#### Découvrez l'état du trafic cycliste aujourd'hui ! :bicyclist:")

with app:
    url = "https://drive.google.com/file/d/1Lsy7Hcjv52H4jrvTNgqznc-hw-mdhljN/view?usp=sharing"
    url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
    token = "pk.eyJ1IjoiY2FtaWxpYWIiLCJhIjoiY2w3a284am1uMDg5ejNvdDV6cWNzdTFsaSJ9.7nOYlVU0P_oLhl-7BnIu6Q"

    df = pd.read_csv(url)
    df["Comptage horaire"] = df["Comptage horaire"].apply(lambda x: round(x,0))
    
    fig = px.scatter_mapbox(df, 
                            lat="Lat",
                            lon="Long", 
                            size="Comptage horaire", 
                            color = "Comptage horaire",
                            hover_name = "Nom du compteur",
                            size_max=35,
                            zoom=11
                            )

    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(width = 800, height = 500)

    st.write(fig)

with dataviz:
    st.markdown("#### Explorer les données ! :rocket:")







