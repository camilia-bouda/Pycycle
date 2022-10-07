import streamlit as st
import pandas as pd
from joblib import load
import gdown
import plotly.express as px
from streamlit_plotly_mapbox_events import plotly_mapbox_events
import json



st.set_page_config(page_title = "Pycycle - Prédiction", layout="wide", initial_sidebar_state="collapsed", page_icon = ":bicyclist:")

header = st.container()
carte = st.container()
graphe_carte = st.container()

with header:
    st.title("Modèles prédictifs")

    st.write("Les modèles établis dans le cadre du projet permettent de prédire\
             le trafic cycliste à Paris\
            à partir de données issues de compteurs à vélos situés un peu\
            partout dans la ville.\n\
            Plus précisément, on cherche à prédire le nombre de vélos circulant\
            comptabilisé soit pour une agrégation de tous les compteurs\
            (trafic général dans Paris), soit pour chacun des compteurs\
            (localisé géographiquement) sur une période de temps définie.")

    tab_global1, tab_global2 = st.tabs(["Prévision du trafic global horaire", "Prévision du trafic par capteur"])
    
    @st.cache(allow_output_mutation=True)
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
    
    @st.cache(allow_output_mutation=True)
    def gdown_joblib(url):
        url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
        output = "model.joblib"
        gdown.download(url, output, quiet=False) 
        model = load(output)
        return model
    
    @st.cache(allow_output_mutation=True)
    def traintestsplit_df_Hour_count(df_Hour_count):
        df_Hour_count = df_Hour_count.sort_values(by = 'Date', ascending = True)
        last_training_index = int(round(df_Hour_count.shape[0]*0.8,0))
        train_set = df_Hour_count.iloc[0:last_training_index, :]
        test_set = df_Hour_count.iloc[last_training_index:,:]
        
        X_train = train_set.drop(['Comptage horaire', 'Date'], axis = 1)
        y_train = train_set['Comptage horaire']
        
        X_test = test_set.drop(['Comptage horaire', 'Date'], axis = 1)
        y_test = test_set['Comptage horaire']
        
        return train_set, test_set, X_train, y_train, X_test, y_test

    @st.cache(allow_output_mutation=True)
    def traintestsplit_df_capteur_tr_horaire(df_capteur_tr_horaire):    
        df_capteur_tr_horaire = df_capteur_tr_horaire.sort_values(by = 'Date', ascending = True)
        df_capteur_tr_horaire = df_capteur_tr_horaire.dropna()
        last_training_index = int(round(df_capteur_tr_horaire.shape[0]*0.8,0))
        train_set = df_capteur_tr_horaire.iloc[0:last_training_index, :]
        test_set = df_capteur_tr_horaire.iloc[last_training_index:,:]
        
        X_train = train_set.drop(['Comptage Tranche Horaire', 'Date'], axis = 1)
        y_train = train_set['Comptage Tranche Horaire']
        
        X_test = test_set.drop(['Comptage Tranche Horaire', 'Date'], axis = 1)
        y_test = test_set['Comptage Tranche Horaire']
        
        return train_set, test_set, X_train, y_train, X_test, y_test

    @st.cache(allow_output_mutation=True)
    def plot_prediction(x_data, pred_data, real_data, titre=""):
        fig = px.bar(x = x_data,
                     y = real_data,
                     opacity=0.7,
                     color_discrete_sequence=['grey'],
                     labels={'x': 'Temps', 'y':'Volume'})
        fig2 = px.scatter(x = x_data,
                         y = pred_data)
        fig.add_trace(fig2.data[0])
        fig.update_layout(width = 800, height = 500)
        fig.update_layout(title= titre)
        
        return fig


    @st.cache(allow_output_mutation=True)
    def calcul_predictions(model, X_train, X_test):
        pred_train = model.predict(X_train)
        pred_test = model.predict(X_test)        

        return pred_train, pred_test





    with tab_global1:
        st.markdown("#### Prévision du niveau de trafic global de la ville par heure")
        st.write("Régressions établies sur les données horaires agrégées disponibles depuis 2019")
        st.write("4 modèles ont été entraînés et les scores (r2 et MAE) obtenus après plusieurs itérations sont les suivants :")
                
        ### dataframe avec les résultats
        df_score_model_global = gdown_csv("https://drive.google.com/file/d/1-AeeyzgZ70KBuS_RVceOajL7wTIabhlf/view?usp=sharing")
        df_score_model_global[["Score_train","Score_test"]] = round(df_score_model_global[["Score_train","Score_test"]],4)
        df_score_model_global[["MAE_train","MAE_test"]] = round(df_score_model_global[["MAE_train","MAE_test"]])
        df_score_model_global = df_score_model_global.astype({"MAE_train" : int,
                                                              "MAE_test" : int})
        df_score_model_global = df_score_model_global.drop([4,5]).reset_index().drop(["index"], axis=1)
        
        st.table(df_score_model_global)
    
        st.write("Avec un entraînement sur un dataset d'une profondeur de près de 3 ans,\
                le modèle Random Forest présente les meilleurs résultats\
                ($r^2$ et erreur absolue moyenne),\
                cependant, on observe un peu d'overfitting sur le dataset de test.\
                \nLes graphiques suivants permettent d'explorer les résultats de\
                fitting et de test de ce modèle.")  
                
        st.markdown("#### Modèle Random Forest")
        
        RF_pred_train = gdown_csv("https://drive.google.com/file/d/1W3sqegoj5jCmGAly-T_VNxr5qn57h5mp/view?usp=sharing")
        RF_pred_test = gdown_csv("https://drive.google.com/file/d/1fScrX7drOsCjajpEyEuhRZgpc6vWv-vv/view?usp=sharing")
        
        RF_pred_train = RF_pred_train.drop_duplicates("Date")
        RF_pred_test = RF_pred_test.drop_duplicates("Date")

        fig_RF_train = plot_prediction(RF_pred_train['Date'],
                                          RF_pred_train['prediction'], RF_pred_train['Comptage horaire'],
                                          "Fitting sur le dataset d'entraînement")
        st.write(fig_RF_train)

        fig_RF_test = plot_prediction(RF_pred_test['Date'],
                                          RF_pred_test['prediction'], RF_pred_test['Comptage horaire'],
                                          "Prévisions sur le dataset de test")
        st.write(fig_RF_test)            
            
    
    with tab_global2:
        st.markdown("#### Prévision du niveau de trafic par capteur, par tranche horaire")
        st.write("Régressions établies par capteur et tranche de 4 heures depuis 2019")
        st.write("4 modèles ont été entraînés et les scores (r2 et MAE) obtenus après plusieurs itérations sont les suivants :")
        
        
        ### dataframe avec les résultats
        df_score_model_capteur = gdown_csv("https://drive.google.com/file/d/1-EiGcmrlx4EigIt71JzvR-uiEaJnszlu/view?usp=sharing")
        df_score_model_capteur[["Score_train","Score_test"]] = round(df_score_model_capteur[["Score_train","Score_test"]],4)
        df_score_model_capteur[["MAE_train","MAE_test"]] = round(df_score_model_capteur[["MAE_train","MAE_test"]])
        df_score_model_capteur = df_score_model_capteur.astype({"MAE_train" : int,
                                                              "MAE_test" : int})
                
        st.table(df_score_model_capteur)


        st.write("Comme pour le modèle agrégé de tous les capteurs,\
                le modèle Random Forest présente les meilleurs résultats\
                ($r^2$ et erreur absolue moyenne),\
                avec un peu d'overfitting sur le dataset de test.\
                \nLes graphiques suivants permettent d'explorer les résultats de\
                fitting et de test de ce modèle par capteur et par tranche de 4 heures.")      
 
    
        st.markdown("#### Modèle Random Forest")
        
        
        RF_pred_train = gdown_csv("https://drive.google.com/file/d/1SR0Efyz0slwaXpT77zb52GUY0fwLTV-n/view?usp=sharing")
        RF_pred_test = gdown_csv("https://drive.google.com/file/d/1--xQjipzWgI5J98zGjzu9G_LL71RERlk/view?usp=sharing")
  
    
        df_capteurs_index = gdown_csv("https://drive.google.com/file/d/1wJvqoWAaCG4x-UDNPppiva47vnsQnV0F/view?usp=sharing")
        id_compteur = 0
        df_capteurs_index =  df_capteurs_index[df_capteurs_index['id compteur'].isin(RF_pred_test["id compteur"].unique())]
        df_capteurs_index =  df_capteurs_index[df_capteurs_index['id compteur'].isin(RF_pred_train["id compteur"].unique())]
        df_capteurs_index["size"] = 5

        token = "pk.eyJ1IjoiY2FtaWxpYWIiLCJhIjoiY2w3a284am1uMDg5ejNvdDV6cWNzdTFsaSJ9.7nOYlVU0P_oLhl-7BnIu6Q"
        


        st.write("Choix du compteur")
        
        fig = px.scatter_mapbox(df_capteurs_index, 
                                lat="Lat",
                                lon="Long", 
                                size="size", 
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

    
        if st.session_state.selected_bike_meter != "[]":  #If a bike meter has been selected, we show the graph of the hourly trafic
            id_compteur = json.loads(st.session_state.selected_bike_meter)[0][0]['pointIndex']
            
            df_tranche_horaire = pd.DataFrame({"Tranche horaire":["Tranche 0","Tranche 1","Tranche 2","Tranche 3","Tranche 4","Tranche 5"],"Heures":["21h - 00h","1h - 4h","5h - 8h","9h - 12h","13h - 16h","17h - 20h"]}).set_index("Tranche horaire")
            st.table(df_tranche_horaire.T)
            
            df_fig_train = RF_pred_train[RF_pred_train["id compteur"] == id_compteur]
            df_fig_train["Tranche Horaire"] = (df_fig_train['Tranche horaire_1']*1 + df_fig_train['Tranche horaire_2']*2 + df_fig_train['Tranche horaire_3']*3 + df_fig_train['Tranche horaire_4']*4 + df_fig_train['Tranche horaire_5']*5)
            df_fig_train["Date - Tranche Horaire"] = df_fig_train["Date"].astype(str) + " - " + df_fig_train["Tranche Horaire"].astype(str)
            df_fig_train = df_fig_train.sort_values(by = ['Date',"Tranche Horaire"], ascending = True)
            df_fig_train = df_fig_train.drop_duplicates("Date - Tranche Horaire")
            
            fig_RF_train = plot_prediction(df_fig_train['Date - Tranche Horaire'],
                                              df_fig_train['prediction'], df_fig_train['Comptage Tranche Horaire'],
                                              "Fitting sur le dataset d'entraînement")
            st.write(fig_RF_train)
        
            df_fig_test = RF_pred_test[RF_pred_test["id compteur"] == id_compteur]
            df_fig_test["Tranche Horaire"] = (df_fig_test['Tranche horaire_1']*1 + df_fig_test['Tranche horaire_2']*2 + df_fig_test['Tranche horaire_3']*3 + df_fig_test['Tranche horaire_4']*4 + df_fig_test['Tranche horaire_5']*5)
            df_fig_test["Date - Tranche Horaire"] = df_fig_test["Date"].astype(str) + " - " + df_fig_test["Tranche Horaire"].astype(str)
            df_fig_test = df_fig_test.sort_values(by = ['Date',"Tranche Horaire"], ascending = True)
            df_fig_test = df_fig_test.drop_duplicates("Date - Tranche Horaire")
         
            fig_RF_test = plot_prediction(df_fig_test['Date - Tranche Horaire'],
                                              df_fig_test['prediction'], df_fig_test['Comptage Tranche Horaire'],
                                              "Prévisions sur le dataset de test")
            st.write(fig_RF_test)
            
        

    
