import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
from datetime import datetime
import json
import gdown
from streamlit_plotly_mapbox_events import plotly_mapbox_events


st.set_page_config(page_title = "Pycycle - Exploration les données du trafic cycliste à Paris", layout="wide", initial_sidebar_state="collapsed", page_icon = ":bicyclist:")

header = st.container()
app = st.container()
dataviz = st.container()


@st.cache()
def load_data(url):
    url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
    df = pd.read_csv(url)

    return df

@st.cache(allow_output_mutation=True)
def gdown_csv(url, separateur=";", index_colonne=0):
    url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
    output = "file.csv"
    gdown.download(url, output, quiet=False) 
    df = pd.read_csv(output, sep=separateur, index_col=index_colonne)
    return df

Jour = {'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi',
        'Sunday': 'Dimanche'}

token = "pk.eyJ1IjoiY2FtaWxpYWIiLCJhIjoiY2w3a284am1uMDg5ejNvdDV6cWNzdTFsaSJ9.7nOYlVU0P_oLhl-7BnIu6Q"
affluence_compteur = load_data("https://drive.google.com/file/d/1-C2wCqL-A0Z07oxqoVSjKk3QZYG8wwcF/view?usp=sharing")
evolution_compteur = load_data("https://drive.google.com/file/d/1-6YJli-DfMveW9fHYySWNK9yYF3-DONY/view?usp=sharing")

affluence_heure = load_data("https://drive.google.com/file/d/1aFA3dbK4VSK2h79UIgM9yTXzpO9gzf2h/view?usp=sharing")
affluence_heure = affluence_heure.reset_index(drop=False)
affluence_heure['Heure'] = affluence_heure['Heure'].astype(str)

df_heure = load_data("https://drive.google.com/file/d/1-5fOWYfR2ly-FTLN3R8TYiXN2F8cspC4/view?usp=sharing")
df_jour = load_data("https://drive.google.com/file/d/1-5buJB2Ex8b_0Mufd8Nx0nosnLDFYH9C/view?usp=sharing")
df_mois = load_data("https://drive.google.com/file/d/1-2EvLeovBozXEo5ZU9Qe-HJOXfRzWW2h/view?usp=sharing")

last_month_affluence = load_data("https://drive.google.com/file/d/1LpNijM6s0J2jUWCiMYNIqitYJXuDwl3I/view?usp=sharing")
last_month_affluence = last_month_affluence[['Jour', 'Heure', 'Nombre de passages horaire moyen']]

df = load_data("https://drive.google.com/file/d/1eyEPpt2vZBTgx-0hjyPwGc23uSqNPYoi/view?usp=sharing")

prediction = df[['Date de comptage', 'Heure', 'Nombre de passages horaire moyen']]
prediction = prediction.loc[(prediction['Date de comptage'] >= '2023-03-20') & (prediction['Date de comptage'] <= '2023-03-26')]
prediction['Jour'] = pd.to_datetime(prediction['Date de comptage']).dt.day_name().map(Jour)
prediction.loc[(prediction['Jour'] == 'Lundi') & (prediction['Heure'].isin([18, 19])), 'Nombre de passages horaire moyen'] = 10

data = df[['Date de comptage', 'Heure', 'Nombre de passages horaire moyen', 'Pluie', 'Jour ferie', 'Petites Vacances', "Vacances d'Été"]]
data = data.loc[data['Date de comptage'] <= '2023-03-15']

data['Année'] = pd.to_datetime(data['Date de comptage']).dt.year
df_annee = data.groupby(['Année']).agg({'Nombre de passages horaire moyen' : 'mean'}).reset_index(drop = False)


with header:
    st.header("Pycycle - Prédiction du trafic cycliste à Paris")
    #st.caption("Camilia Bouda, Gilles Schenfele")
    st.subheader("#### :bicyclist:  Découvrez l'état du trafic cycliste aujourd'hui !")
    st.write('')
    st.info("Sélectionner un jour de la semaine et un compteur sur la carte pour voir son affluence habituelle au fil de la journée", icon="⬇️")
    if 'selected_bike_meter' not in st.session_state:
        st.session_state.selected_bike_meter = '[]'    




with app:
    tz = pytz.timezone('Europe/Paris')
    hour = datetime.now(tz).hour
    day_index = int(datetime.now(tz).strftime("%u")) - 1
        
    st.radio(label= 'Jour de la semaine', options=('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'),
            index=day_index, key='day', horizontal = True)
    
    filtered_df = affluence_compteur[affluence_compteur['Jour Type'] == st.session_state.day]
    filtered_df = filtered_df.rename(columns={'Comptage horaire': 'Comptage horaire moyen'})
    filtered_df = filtered_df.reset_index(drop=False)


    col1, col2 = st.columns((1.7, 1.5), gap="medium")

    with col1:
        fig = px.scatter_mapbox(filtered_df, 
                                lat="Lat",
                                lon="Long", 
                                size="Comptage horaire moyen", 
                                color = "Comptage horaire moyen",
                                hover_name = "Nom du compteur",
                                hover_data = ['Jour Type'],
                                size_max=30,
                                zoom=11,
                                title="Affluence horaire habituelle")

        fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_layout(height = 400)
        fig.update_coloraxes(showscale=False)

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
            usual_affluence = last_month_affluence.loc[(last_month_affluence['Jour'] == st.session_state.day) &\
                 (last_month_affluence['Heure'] == hour), 'Nombre de passages horaire moyen'].values[0]
            predicted_affluence = prediction.loc[(prediction['Jour'] == st.session_state.day) & (prediction['Heure'] == hour), 'Nombre de passages horaire moyen'].values[0]
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
            fig2.update_layout( height = 290,
                                showlegend=False, 
                                xaxis={'title': '','visible': True, 'showticklabels': True},
                                yaxis={"visible": False})

            affluence = str(filtered_df2.loc[affluence_heure['Heure'] == str(hour)]['Affluence']).split('\n')[0].split('  ')[-1]
            texte = "🕑 " + st.session_state.day+ " - " + str(hour) + 'h: Habituellement **' + affluence.lower() + "**"

            st.markdown("📍 " + selected_compteur_name)
            st.markdown(texte)

            difference = round(100*(usual_affluence - predicted_affluence)/usual_affluence, 2)

            if abs(difference) >= 10:
                if difference < 0:
                    TR = "Selon nos prévisions, le trafic est plus dense que la normale."
                    st.warning(TR, icon="🤖")
                else:
                    TR = "Selon nos prévisions, le trafic est moins dense que la normale."
                    st.success(TR, icon = "🤖")
            else:
                TR = "Trafic habituel"
                st.info(TR, icon = "🤖")

            st.plotly_chart(fig2, use_container_width=True, config = {'displayModeBar': False})




with dataviz:
    st.subheader("#### :rocket: Explorer les données !")

    st.write("Nous vous proposons d'explorer les données du trafic cycliste parisien habituel en fonction du niveau d'agrégation (par heure, type de jour, mois et année)\
        et de paramètres extérieurs tel que l'effet de la pluie.\
            Vous pouvez également voir l'évolution du trafic moyen à l'échelle d'une journée dans le dernier onglet ci-dessous.\
                \nBonne exploration !🧑‍🚀")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Heure", "Jour", "Mois", "Année", "Animation - Evolution du trafic au cours d'une journée"])

    with tab1:

        c2, c1 = st.columns((2, 0.5))

        with c1:
            st.info("Sélectionner les paramètres pour voir leur influence sur le trafic cycliste:", icon="⬇️")
            weather_checkbox = st.checkbox("☔️ Pluie", value=False, key='wc1')
            holiday_checkbox = st.checkbox("🌴 Vacances et jours fériés", value=False, key='hc1')


        with c2:
            df1 = df_heure[(df_heure['météo'] == "Pas de pluie") & (df_heure['Vacances et jours fériés'] == 0)]
            df2 = df_heure[(df_heure['météo'] == "Pluie") & (df_heure['Vacances et jours fériés'] == 0)]
            df3 = df_heure[(df_heure['météo'] == "Pas de pluie") & (df_heure['Vacances et jours fériés'] == 1)]

            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x = df1["Heure"], y=df1['Comptage horaire'], name='Pas de pluie et hors vacances/jours fériés'))

            if weather_checkbox:
                fig3.add_trace(go.Bar(x = df2["Heure"], y=df2['Comptage horaire'], name='Pluie'))
            
            if holiday_checkbox:
                fig3.add_trace(go.Bar(x = df3["Heure"], y=df3['Comptage horaire'], name='Vacances et jours fériés'))
            
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig3.update_layout(xaxis = dict(tickmode = 'array', tickvals = [i for i in range(24)],ticktext = [str(i) + "h" for i in range(24)]))
            fig3.update_layout(xaxis={'title': '','visible': True, 'showticklabels': True}, yaxis={"visible": True})
            fig3.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0))


            st.markdown("**Comptage horaire moyen par heure**")
            st.plotly_chart(fig3, use_container_width=True)
            
    

    with tab2:
        c2, c1 = st.columns((2, 0.5))

        with c1:
            st.info("Sélectionner les paramètres pour voir leur influence sur le trafic cycliste:", icon="⬇️")
            weather_checkbox = st.checkbox("☔️ Pluie", value=False, key = 'wc2')
            holiday_checkbox = st.checkbox("🌴 Vacances et jours fériés", value=False, key = 'hc2')


        with c2:
            df1 = df_jour[(df_jour['météo'] == "Pas de pluie") & (df_jour['Vacances et jours fériés'] == 0)]
            df2 = df_jour[(df_jour['météo'] == "Pluie") & (df_jour['Vacances et jours fériés'] == 0)]
            df3 = df_jour[(df_jour['météo'] == "Pas de pluie") & (df_jour['Vacances et jours fériés'] == 1)]

            fig4 = go.Figure()
            fig4.add_trace(go.Bar(x = df1["Jour Type"], y=df1['Comptage horaire'], name='Pas de pluie et hors vacances/jours fériés'))

            if weather_checkbox:
                fig4.add_trace(go.Bar(x = df2["Jour Type"], y=df2['Comptage horaire'], name='Pluie'))
            
            if holiday_checkbox:
                fig4.add_trace(go.Bar(x = df3["Jour Type"], y=df3['Comptage horaire'], name='Vacances et jours fériés'))
            
            fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            fig4.update_layout(xaxis={'title': '','visible': True, 'showticklabels': True}, yaxis={"visible": True})
            fig4.update_layout(legend=dict(yanchor="top", y=1.1, xanchor="left", x=0))


            st.markdown("**Comptage horaire moyen par type de jour**")
            st.plotly_chart(fig4, use_container_width=True)
    

    with tab3:
        fig5 = px.bar(df_mois, x = "Mois", y='Comptage horaire', barmode='group')

        fig5.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        fig5.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig5.update_layout(xaxis={'title': '','visible': True, 'showticklabels': True}, yaxis={"visible": True, 'title': ''})
        
        st.markdown("**Comptage horaire moyen par mois**")
        st.plotly_chart(fig5, use_container_width=True)
    

    with tab4:
        fig6 = px.bar(df_annee, x = "Année", y='Nombre de passages horaire moyen', barmode='group')

        fig6.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        fig6.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig6.update_layout(xaxis={'title': '','visible': True, 'showticklabels': True}, yaxis={"visible": True, 'title': ''})
        fig6.update_layout(xaxis = dict(tickmode = 'array', tickvals = [2019, 2020, 2021, 2022, 2023],ticktext = ['2019', '2020', '2021', '2022', '2023']))

        st.markdown("**Comptage horaire moyen par année**")
        st.plotly_chart(fig6, use_container_width=True)

    
    with tab5:
        fig7 = px.scatter_mapbox(evolution_compteur, 
                                lat="Lat",
                                lon="Long", 
                                size="Comptage horaire moyen", 
                                color = "Comptage horaire moyen",
                                hover_name = "Nom du compteur",
                                size_max=40,
                                zoom=11,
                                title="Affluence horaire habituelle",
                                animation_frame="Heure",
                                animation_group="Comptage horaire moyen")

        fig7.update_layout(mapbox_style="light", mapbox_accesstoken=token)
        fig7.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig7.update_layout(height = 600)

        st.markdown("**Evolution du comptage horaire moyen par compteur au fil d'une journée**")
        st.plotly_chart(fig7, use_container_width=True)



with st.sidebar:
    st.caption("Pycycle - Prédiction du trafic cycliste à Paris \n Auteurs: Camilia Bouda, Gilles Schenfele")






