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

    with tab_global1:
        st.markdown("#### Prévision du niveau de trafic global de la ville par heure")
        st.text("Régressions établies sur les données horaires agrégées disponibles depuis 2019")
        st.text("4 modèles ont été entraînés et les scores (r2 et MAE) obtenus après\n plusieurs itérations sont les suivants :")
        

        
        
        ### data du modele (dataset entrainement et dataset de test)
        url1 = "https://drive.google.com/file/d/1h_JNUIUM3dtvWVnd8aRpmt-HDWFB8pv5/view?usp=sharing"
        url1 = 'https://drive.google.com/uc?id=' + url1.split('/')[-2]
        output1 = "file1.csv"
        gdown.download(url1, output1, quiet=False) 
        df_Hour_count = pd.read_csv(output1, sep=";", index_col=0)
        
        df_Hour_count = df_Hour_count.sort_values(by = 'Date', ascending = True)
        last_training_index = int(round(df_Hour_count.shape[0]*0.8,0))
        train_set = df_Hour_count.iloc[0:last_training_index, :]
        test_set = df_Hour_count.iloc[last_training_index:,:]
        
        X_train = train_set.drop(['Comptage horaire', 'Date'], axis = 1)
        y_train = train_set['Comptage horaire']
        
        X_test = test_set.drop(['Comptage horaire', 'Date'], axis = 1)
        y_test = test_set['Comptage horaire']      

        ### dataframe avec les résultats
        url = "https://drive.google.com/file/d/1vSWvb_q9C2Xfh0bnoMQm5FDCkM-N5CfU/view?usp=sharing"
        url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
        output = "file.csv"
        gdown.download(url, output, quiet=False) 
        df_score_model_global = pd.read_csv(output, sep=";", index_col=0)
        
        st.table(df_score_model_global)
    
        tab1, tab2, tab3, tab4 = st.tabs(["Lasso", "Ridge", "Elastic Net CV", "Random Forest"])
    
        with tab1:
            st.markdown("#### Régression Lasso")
            
            url = "https://drive.google.com/file/d/1--uJQdiPpAsOf2IeSOJ5Jt781dqoA2p-/view?usp=sharing"
            url = "https://drive.google.com/uc?id=" + url.split('/')[-2]
            output = "model.joblib"
            gdown.download(url, output, quiet=False)
            model_global_lasso = load(output)
            
            lasso_pred_train = model_global_lasso.predict(X_train)
            lasso_pred_test = model_global_lasso.predict(X_test)
            
            st.text("score sur le dataset d'entraînement : " +  str(model_global_lasso.score(X_train,y_train)))
            st.text("score sur le dataset de test : " + str(model_global_lasso.score(X_test,y_test)))
        
            
        
            fig = px.scatter(x = train_set['Date'],
                             y = lasso_pred_train)
            fig2 = px.bar(x = train_set['Date'],
                          y = y_train)
            fig.add_trace(fig2.data[0])
            fig.update_layout(width = 800, height = 500)
            fig.update_layout(title= "Fitting sur le dataset d'entraînement")
            st.write(fig)
            
            
            fig = px.scatter(x = test_set['Date'],
                             y = lasso_pred_test)
            fig2 = px.bar(x = test_set['Date'],
                          y = y_test)
            fig.add_trace(fig2.data[0])
            fig.update_layout(width = 800, height = 500)
            fig.update_layout(title= "Prévisions sur le dataset de test")
            st.write(fig)
            
        
        with tab2:
            st.markdown("#### Régression Ridge")

            #url = format(str('https://drive.google.com/file/d/1-5d4mOyc-Wp3uERBOdML9MsxdMAAzZF5/view?usp=sharing'))
            #url = 'https://drive.google.com/uc?id=' + url.split('/')[-2] 
            #model_global_ridge = load(url)
            #st.text(model_global_ridge.score)
        
        with tab3:
            st.markdown("#### Régression Elastic Net CV")

            #url = "https://drive.google.com/file/d/1-A-Ipr2WjKjtxIvQ3k6Z9ANXVbgirWP3/view?usp=sharing"
            #url = "https://drive.google.com/uc?id=" + url.split('/')[-2] 
            #model_global_lasso = load(url)
            #st.text(model_global_lasso.score)
            
        with tab4:
            st.markdown("#### Régression Random Forest")

            #url = "https://drive.google.com/file/d/1-ANJZ8FZnR5GLw1FyDTSF6Y0QocIGHNp/view?usp=sharing"
            #url = "https://drive.google.com/uc?id=" + url.split('/')[-2] 
            #model_global_lasso = load(url)
            #st.text(model_global_lasso.score)
        
    
    with tab_global2:
        st.markdown("#### Prévision du niveau de trafic par capteur, par tranche horaire")
        st.text("Régressions établies par capteur et tranche de 4 heures depuis 2019")
        st.text("4 modèles ont été entraînés et les scores (r2 et MAE) obtenus après\n plusieurs itérations sont les suivants :")
        

        
        
        ### data du modele (dataset entrainement et dataset de test)
        url2 = "    "
        url2 = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
        output2 = "file2.csv"
        gdown.download(url2, output2, quiet=False)        
        df_capteur_tr_horaire = pd.read_csv(output2, sep=";", index_col=0)
        
        df_capteur_tr_horaire = df_capteur_tr_horaire.sort_values(by = 'Date', ascending = True)
        df_capteur_tr_horaire = df_capteur_tr_horaire.dropna()
        last_training_index = int(round(df_capteur_tr_horaire.shape[0]*0.8,0))
        train_set = df_capteur_tr_horaire.iloc[0:last_training_index, :]
        test_set = df_capteur_tr_horaire.iloc[last_training_index:,:]
        
        X_train = train_set.drop(['Comptage Tranche Horaire', 'Date'], axis = 1)
        y_train = train_set['Comptage Tranche Horaire']
        
        X_test = test_set.drop(['Comptage Tranche Horaire', 'Date'], axis = 1)
        y_test = test_set['Comptage Tranche Horaire']     


        ### dataframe avec les résultats
        url = "https://drive.google.com/file/d/1-EiGcmrlx4EigIt71JzvR-uiEaJnszlu/view?usp=sharing"
        url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
        output = "file.csv"
        gdown.download(url, output, quiet=False)
        df_score_model_capteur = pd.read_csv(output, sep=";", index_col=0)
        
        st.table(df_score_model_capteur)
    
        tab1, tab2, tab3, tab4 = st.tabs(["Lasso", "Ridge", "Elastic Net CV", "Random Forest"])
    
        with tab1:
            st.markdown("#### Régression Lasso")
            
        
        
        with tab2:
            st.markdown("#### Régression Ridge")


        
        with tab3:
            st.markdown("#### Régression Elastic Net CV")


            
        with tab4:
            st.markdown("#### Régression Random Forest")

