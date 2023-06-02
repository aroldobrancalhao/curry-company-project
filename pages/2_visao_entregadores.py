#Libraries
import pandas as pd
import re
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='🛵', layout='wide' )

# ==================================================== 
# Funções
# ==================================================== 

def top_delivers( df1, top_asc ):
    df2 = df1.loc[:, ['Time_taken(min)', 'Delivery_person_ID', 'City']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()
    df_aux_01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux_02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux_03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux_01, df_aux_02, df_aux_03]).reset_index(drop=True)
    return df3

def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe
        
        Tipos de Limpeza:
        1.Remoção dos dados NaN
        2.Mudança do tipo da coluna de dados
        3.Remoção dos espaços das variaveis
        4.Foramatação da coluina de datas
        5.Limpeza da coluna de tempo ( remoção do texto da variavel numerica

        Input: Dataframe
        Output: Dataframe        
    """
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    
    #
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    # Comando para remover o texto de números
    df1 = df1.reset_index( drop=True )
        
    # Remover spaco da string
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    
    #limpando a coluna de 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.findall(r'\d+').str.join('').astype(int)
    
    return df1
# ============Inicio da Estrutura logica do código============== 
    
# ==================================================== 
#                  import dataset
# ==================================================== 
df = pd.read_csv( 'dataset/train.csv' )
df1 = df.copy()

# ==================================================== 
#                  Limpando Dados                  
# ==================================================== 
df1 = clean_code( df )


# ==================================================== 
#                  BARRA LATERAL                    
# ==================================================== 
st.header('Marketplace - Visão Entregadores')

#image_path = 'teste.jpg'
image = Image.open( 'logo.jpg' )
st.sidebar.image( image, width=180)

st.sidebar.markdown( '# Cury Company')
st.sidebar.markdown( '## Fast Delivery in Town')
st.sidebar.markdown( """___""")
st.sidebar.markdown('## Seleciona uma data limite')
date_slider = st.sidebar.slider(
     'Até qual data?',
     value=datetime(2022, 4, 13),
     min_value=datetime(2022, 2, 11),
     max_value=datetime(2022, 4, 6),
     format='DD-MM-YYYY')

st.sidebar.markdown( """___""")

condition_options = st.sidebar.multiselect(
    'Quais as condições do clima',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

st.sidebar.markdown( """___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do clima',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown( """___""")

st.sidebar.markdown( '### Powered by Comunidade DS')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionada = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionada, :]

#filtro clima
linhas_selecionada = df1['Weatherconditions'].isin( condition_options )
df1 = df1.loc[linhas_selecionada, :]

#st.dataframe(df1)

#st.header ('teste de edição')

# ==================================================== 
#                  lAYOUT NO STREAMLIT                    
# ==================================================== 

tab1, tab2, tab3  =st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.header('Métricas Gerias')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
           # A maior idade dos entregadores
            maior_idade = df1.loc[:, "Delivery_person_Age"].max()
            col1.metric( 'Maior de Idade', maior_idade )

        with col2:
            # A menor idade dos entregadores
            menor_idade = df1.loc[:, "Delivery_person_Age"].min()
            col2.metric( 'Menor de Idade', menor_idade )

        with col3:
            # A melhor condição do veiculo
            melhor_condicao = df1.loc[:, "Vehicle_condition"].max()
            col3.metric( 'Melhor condição', melhor_condicao )

        with col4:
            # A Pior condição do veiculo
            pior_condicao = df1.loc[:, "Vehicle_condition"].min()
            col4.metric( 'Pior condição', pior_condicao )

    with st.container():
        st.markdown("""___""")
        st.title( 'Avaliações' )

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Avaliação medias por entregador')
            df_avg_ratings_per_delivery = df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]. groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe( df_avg_ratings_per_delivery )

        with col2:
            st.markdown('##### Avaliação media por transito')
            df_avg_std_rating_by_traffic = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']})
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe( df_avg_std_rating_by_traffic )
            st.markdown('##### Avaliação media por clima')
            df_avg_std_rating_by_weather = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe( df_avg_std_rating_by_weather )

    with st.container():
        st.markdown("""___""")
        st.title( 'Velocidade de Entrega' )

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Top entregadores mais rapidos')
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )            

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )
            
