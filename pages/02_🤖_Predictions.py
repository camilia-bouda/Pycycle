import streamlit as st
import pandas as pd
from joblib import load
import gdown
import plotly.express as px



st.set_page_config(page_title = "Pycycle")

header = st.container()

with header:
    st.title("Modèles prédictifs")

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
                     color_discrete_sequence=['grey'])
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
                
        
        ### data du modele horaire agrégé à la ville (dataset entrainement et dataset de test)
        df_Hour_count = gdown_csv("https://drive.google.com/file/d/1tSDX-jjYRku5hNWNkXTKM6hyC25KcuW1/view?usp=sharing")
        
        ### split des datas
        train_set_Hour_count, test_set_Hour_count, X_train_Hour_count, y_train_Hour_count, X_test_Hour_count, y_test_Hour_count = traintestsplit_df_Hour_count(df_Hour_count)
    

        ### dataframe avec les résultats
        df_score_model_global = gdown_csv("https://drive.google.com/file/d/1-AeeyzgZ70KBuS_RVceOajL7wTIabhlf/view?usp=sharing")
        df_score_model_global[["Score_train","Score_test"]] = round(df_score_model_global[["Score_train","Score_test"]],4)
        df_score_model_global[["MAE_train","MAE_test"]] = round(df_score_model_global[["MAE_train","MAE_test"]])
        df_score_model_global = df_score_model_global.astype({"MAE_train" : int,
                                                              "MAE_test" : int})
        
        
        st.table(df_score_model_global)
        
        st.markdown("#### Modèle Random Forest")
        
        
        if st.button('Charger le modele'): 
        
            model_global_RF = gdown_joblib("https://drive.google.com/file/d/1pt4Dg9MokgAUrhlaR8codl-3WScaSjDv/view?usp=sharing")
            RF_pred_train, RF_pred_test = calcul_predictions(model_global_RF, X_train_Hour_count, X_test_Hour_count)
            
            st.write("score sur le dataset d'entraînement : " +  str(round(model_global_RF.score(X_train_Hour_count,y_train_Hour_count),4)))
            st.write("score sur le dataset de test : " + str(round(model_global_RF.score(X_test_Hour_count,y_test_Hour_count),4)))
        
            
            
            fig_RF_train = plot_prediction(train_set_Hour_count['Date'],
                                              RF_pred_train, y_train_Hour_count,
                                              "Fitting sur le dataset d'entraînement")
            st.write(fig_RF_train)
    
            fig_RF_test = plot_prediction(test_set_Hour_count['Date'],
                                              RF_pred_test, y_test_Hour_count,
                                              "Prévisions sur le dataset de test")
            st.write(fig_RF_test)            
            
        else:
            st.write("Charger le modèle Random Forest (env. 600Mo, temps de chargement d'une minute)")
             
    
    
    with tab_global2:
        st.markdown("#### Prévision du niveau de trafic par capteur, par tranche horaire")
        st.write("Régressions établies par capteur et tranche de 4 heures depuis 2019")
        st.write("4 modèles ont été entraînés et les scores (r2 et MAE) obtenus après plusieurs itérations sont les suivants :")
        

        ### data du modele par capteur et tranches horaires (dataset entrainement et dataset de test)
        df_capteur_tr_horaire = gdown_csv("https://drive.google.com/file/d/1-2u6zMBGQBqGp1nRHpy7IQu1OO9C6YRq/view?usp=sharing")
        
        
        ### split des datas
        train_set_capteur_tr_horaire, test_set_capteur_tr_horaire, X_train_capteur_tr_horaire, y_train_capteur_tr_horaire, X_test_capteur_tr_horaire, y_test_capteur_tr_horaire = traintestsplit_df_capteur_tr_horaire(df_capteur_tr_horaire)
        
        train_set_capteur_tr_horaire["Date - Tranche Horaire"] = train_set_capteur_tr_horaire["Date"].astype(str) + " - " + (train_set_capteur_tr_horaire['Tranche horaire_1']*1 + train_set_capteur_tr_horaire['Tranche horaire_2']*2 + train_set_capteur_tr_horaire['Tranche horaire_3']*3 + train_set_capteur_tr_horaire['Tranche horaire_4']*4 + train_set_capteur_tr_horaire['Tranche horaire_5']*5).astype(str)
        test_set_capteur_tr_horaire["Date - Tranche Horaire"] = test_set_capteur_tr_horaire["Date"].astype(str) + " - " + (test_set_capteur_tr_horaire['Tranche horaire_1']*1 + test_set_capteur_tr_horaire['Tranche horaire_2']*2 + test_set_capteur_tr_horaire['Tranche horaire_3']*3 + test_set_capteur_tr_horaire['Tranche horaire_4']*4 + test_set_capteur_tr_horaire['Tranche horaire_5']*5).astype(str)

        ### dataframe avec les résultats
        df_score_model_capteur = gdown_csv("https://drive.google.com/file/d/1-EiGcmrlx4EigIt71JzvR-uiEaJnszlu/view?usp=sharing")
        df_score_model_capteur[["Score_train","Score_test"]] = round(df_score_model_capteur[["Score_train","Score_test"]],4)
        df_score_model_capteur[["MAE_train","MAE_test"]] = round(df_score_model_capteur[["MAE_train","MAE_test"]])
        df_score_model_capteur = df_score_model_capteur.astype({"MAE_train" : int,
                                                              "MAE_test" : int})
                
        st.table(df_score_model_capteur)
    
   
        st.markdown("#### Modèle Random Forest")
        
        
        if st.button('Charger le modèle'):        
            model_capteur_RF = gdown_joblib("https://drive.google.com/file/d/1-AQqkeCysg5BN2ZQoqz5J1i5Y1xA0uKZ/view?usp=sharing")
            RF_pred_train, RF_pred_test = calcul_predictions(model_capteur_RF, X_train_capteur_tr_horaire, X_test_capteur_tr_horaire)
            
            st.write("score sur le dataset d'entraînement : " +  str(round(model_capteur_RF.score(X_train_capteur_tr_horaire,y_train_capteur_tr_horaire),4)))
            st.write("score sur le dataset de test : " + str(round(model_capteur_RF.score(X_test_capteur_tr_horaire,y_test_capteur_tr_horaire),4)))

        else:
            st.write("Charger le modèle Random Forest (env. 4Go, temps de chargement de quelques minutes)")
 

        st.write("Tranche 0 : 21h - 1h, Tranche 1 : 1h - 4h, Tranche 2 : 5h - 8h, Tranche 3 : 9h - 12h, Tranche 4 : 13h - 16h, Tranche 5 : 17h - 20h")
    
        df_capteurs_index = gdown_csv("https://drive.google.com/file/d/1wJvqoWAaCG4x-UDNPppiva47vnsQnV0F/view?usp=sharing")
        
        id_compteur = 0
        
        df_capteurs_index = df_capteurs_index[df_capteurs_index['id compteur'].isin(test_set_capteur_tr_horaire["id compteur"].unique())]
        
        select_capteur = st.selectbox('Choix du capteur (temps de calcul d\'une à deux minutes)', df_capteurs_index['Capteur'])
        
        id_compteur = df_capteurs_index.loc[df_capteurs_index['Capteur']==select_capteur, "id compteur"].values[0]
        
        df_fig_train = train_set_capteur_tr_horaire
        df_fig_train["Prevision"] = pd.Series(RF_pred_train)
        df_fig_train["Reel"] = y_train_capteur_tr_horaire
        df_fig_train = df_fig_train[df_fig_train["id compteur"] == id_compteur]
        df_fig_train["Tranche Horaire"] = (df_fig_train['Tranche horaire_1']*1 + df_fig_train['Tranche horaire_2']*2 + df_fig_train['Tranche horaire_3']*3 + df_fig_train['Tranche horaire_4']*4 + df_fig_train['Tranche horaire_5']*5)
        df_fig_train = df_fig_train.sort_values(by = ['Date',"Tranche Horaire"], ascending = True)
        ### drop duplicates car il y a un soucis dans le dataset avec les tranches historiques ?
        # df_fig_train = df_fig_train.drop_duplicates(subset=["Date","Tranche Horaire"])
        
        fig_RF_train = plot_prediction(df_fig_train['Date - Tranche Horaire'],
                                          df_fig_train['Prevision'], df_fig_train['Reel'],
                                          "Fitting sur le dataset d'entraînement")
        st.write(fig_RF_train)

        df_fig_test = test_set_capteur_tr_horaire
        df_fig_test["Prevision"] = pd.Series(RF_pred_test)
        df_fig_test["Reel"] = y_test_capteur_tr_horaire
        df_fig_test = df_fig_test[df_fig_test["id compteur"] == id_compteur]
        df_fig_test["Tranche Horaire"] = (df_fig_test['Tranche horaire_1']*1 + df_fig_test['Tranche horaire_2']*2 + df_fig_test['Tranche horaire_3']*3 + df_fig_test['Tranche horaire_4']*4 + df_fig_test['Tranche horaire_5']*5)
        df_fig_test = df_fig_test.sort_values(by = ['Date',"Tranche Horaire"], ascending = True)
        ### drop duplicates car il y a un soucis dans le dataset avec les tranches historiques ?
        # df_fig_test = df_fig_test.drop_duplicates(subset=["Date","Tranche Horaire"])
        
        if len(df_fig_test) == 0:
            st.write("Ce capteur est absent du dataset de test")
            
        else:
        
            fig_lasso_test = plot_prediction(df_fig_test['Date - Tranche Horaire'],
                                              df_fig_test['Prevision'], df_fig_test['Reel'],
                                              "Fitting sur le dataset d'entraînement")
            st.write(fig_lasso_test)   
                
        

    
