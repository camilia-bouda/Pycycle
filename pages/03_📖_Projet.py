import streamlit as st
import pandas as pd
import gdown
import plotly.express as px
from streamlit_plotly_mapbox_events import plotly_mapbox_events
from PIL import Image

st.set_page_config(page_title = "Pycycle", layout="wide", initial_sidebar_state="collapsed", page_icon = ":bicyclist:")

header = st.container()


with header:
    
    @st.cache(allow_output_mutation=True)
    def gdown_csv(url, separateur=";", index_colonne=0):
        url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
        output = "file.csv"
        gdown.download(url, output, quiet=False) 
        df = pd.read_csv(output, sep=separateur, index_col=index_colonne)
        return df    

    st.title("Construction des modèles")
    st.markdown("### Contexte du projet")
    st.write("L’objectif de ce projet est de prédire le trafic cycliste à Paris\
            à partir de données issues de compteurs à vélos situés un peu\
            partout à Paris.\n\
            Plus précisément, on cherche à prédire le nombre de vélos circulant\
            comptabilisé soit pour une agrégation de tous les compteurs\
            (trafic général dans Paris), soit pour chacun des compteurs\
            (localisé géographiquement) sur une période de temps définie.")
    
    st.markdown('### Jeu de données initial')
    st.write("Le dataset original sur lequel est basé notre projet est issu\
            de l’[Open Data de la Mairie de Paris](https://opendata.paris.fr/explore/dataset/comptage-velo-donnees-compteurs/information/?disjunctive.id_compteur&disjunctive.nom_compteur&disjunctive.id&disjunctive.name)\
            et présente des données de comptages horaires du trafic cycliste\
            sur 13 mois glissants. La structure des données est la suivante :")
            
    df_format_data = pd.DataFrame({"Champs":["Identifiant du compteur",
                                   "Nom du compteur : données complètes comportant l’adresse postale et le sens de comptage",
                                   "Identifiant du site de comptage",
                                   "Nom du site de comptage",
                                   "Comptage horaire : le volume de cycliste en une heure --→ variable cible",
                                   "Date et heure de comptage : données complètes comporte la date et l’heure du comptage horaire",
                                   "Date d'installation du site de comptage",
                                   "Lien vers photo du site de comptage",
                                   "Coordonnées géographiques : coordonnées au format GPS du compteur",
                                   "Identifiant technique compteur"]})
    st.table(df_format_data)
            
    st.write("Nous avons également récupéré les données des années précédentes\
            jusqu'en 2018 également disponible sur l’Open Data de la Mairie de Paris.\
            \nLe jeu de données est alors composé d’environ 2 500 000 lignes.")
    
    st.markdown('### Sélection des compteurs')
    df_compteurs_selection = gdown_csv("https://drive.google.com/file/d/1wJvqoWAaCG4x-UDNPppiva47vnsQnV0F/view?usp=sharing")
    df_compteurs_all = gdown_csv("https://drive.google.com/file/d/1JQOWtGU12_70PQcs0ayBgYs0-qPbZNqZ/view?usp=sharing")
    df_compteurs_all = df_compteurs_all.merge(df_compteurs_selection, how="outer")
    df_compteurs_all.loc[df_compteurs_all["id compteur"].notnull(),"selection"] = "Selectionnés"
    df_compteurs_all.loc[df_compteurs_all["id compteur"].isna(),"selection"] = "Ecartés"
    df_compteurs_all["size"]=5
    
    token = "pk.eyJ1IjoiY2FtaWxpYWIiLCJhIjoiY2w3a284am1uMDg5ejNvdDV6cWNzdTFsaSJ9.7nOYlVU0P_oLhl-7BnIu6Q"

    st.write("Le dataset original (sur l’année 2021) permet d’identifier près d'une centaine\
            compteurs dans Paris. Néanmoins, certains compteurs ont été enlevés,\
            ajoutés ou remplacés au fil du temps depuis 2019. Afin d’avoir des\
            observations cohérentes au fil du temps, il est nécessaire de\
            ne conserver que les compteurs présents en 2019 et toujours présents\
            aujourd’hui. Un filtre est donc appliqué pour ne retenir que les\
            capteurs remplissant cette condition")

    fig = px.scatter_mapbox(df_compteurs_all, 
                            lat="Lat",
                            lon="Long", 
                            size="size",
                            color="selection",
                            hover_name = "Nom du compteur",
                            size_max=10,
                            zoom=11)

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
    
    st.markdown('### Enrichissement des données')
    
    st.write("Les données initiales permettent de renseigner les comptages en fonction :\
            \n ● De la temporalité connu avec l'horodatage du comptage (jour de la semaine, mois, année) \
            \n ● De la géographie avec la position des compteurs (coordonnées GPS) et la direction du comptage\
            \n\
            \nLe trafic cycliste est également influencé par d'autres facteurs que nous avons\
            intégrés au jeu de donnée :\
            \n ● Un contexte calendaire : vacances scolaires, jours fériés récupérés sur l'[Open Data du ministère de l'Education Nationale](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/information/?disjunctive.description&disjunctive.population&disjunctive.location&disjunctive.zones&disjunctive.annee_scolaire&sort=end_date&calendarview=month)\
            \n ● Des évènements particuliers : confinement (ajout manuel du 17/03/2020 au 10/05/2020),\
                Grève importante des transports publics (ajout manuel pour le mois de décembre 2019)\
            \n ● La météo : opinion météo de la journée, température moyenne, précipitation récupérés en [Open Data](https://www.historique-meteo.net/france/ile-de-france/paris/)\
            \n ● Des aménagements cyclables autour de chaque compteur, dont la longueur\
                cumulée de pistes cyclables a été calculée dans un rayon d'environ 1 km a été calculée à partir\
                des données de l'[Open Data de la Ville de Paris](https://opendata.paris.fr/explore/dataset/reseau-cyclable/information/?disjunctive.typologie_simple&disjunctive.bidirectionnel&disjunctive.statut&disjunctive.sens_velo&disjunctive.voie&disjunctive.arrdt&disjunctive.bois&disjunctive.position&disjunctive.circulation&disjunctive.piste&disjunctive.couloir_bus&disjunctive.type_continuite&disjunctive.reseau)\
            \n ● Des Points d'Intérêt (musée, sites touristiques,...) autour de chaque compteur récupérés\
                sur l'[Open Data de la Région Ile-de-France](https://data.iledefrance.fr/explore/dataset/principaux-sites-touristiques-en-ile-de-france0/information/)\
            ")
    
    st.markdown('### Traitement des données')
    
    st.markdown('### Les modèles testés')
    
    st.write("Dans un premier temps lors du projet, nous nous sommes concentrés\
            sur la prédiction du trafic des vélos à une échelle agrégée pour\
            tous les compteurs (trafic général dans Paris, sans distinction géographique).\
            \nDans un second temps, en fin de projet, nous avons commencé à construire des\
            modélisations afin de réaliser une prédiction du trafic des vélos par capteur (localisé\
            géographiquement) sur une période de temps définie.")
    st.write("Différents modèles de régression ont été testés et enrichis par itération\
            ainsi que des modèles de classification.\
            \nFinalement, ceux sont les modèles de régression Random Forest qui ont permis\
            d'obtenir les meilleurs résultats.")
    schema_modeles = Image.open("pages/schema_evolution_modelisation.png")
    st.image(schema_modeles)
    

    
    

    st.markdown('### Perspectives')