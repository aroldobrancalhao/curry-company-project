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
import numpy as np

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide' )

# ==================================================== 
# Funções
# ==================================================== 

def avg_std_time_on_traffic( df1 ):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def festival( df1, fest, avg_mean):
    """
        Está função calcila o tempo medio e desvio padrão do tempo de entrega durante o festival e não festival
        Parametros
            Input:
                - df: Dataframe com os dados necessarios para os dados
                - fest: Festival com ou sem festival
                    'Yes' ou 'No'
                - avg_mean: Tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tempo medio
                    'std_time': calcula o desvio padrão
            Output:
                - df: Dataframe com 2 colunas e duas linhas
    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == fest, avg_mean], 2 )
    return df_aux

def distance( df1, fig ):
    if fig == False:
        col = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, col].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round( df1['distance'].mean(), 2 )
        
        return avg_distance

    else:
        df1['distance'] = df1.loc[:, ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
    return fig

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
st.header('Marketplace - Visão Restaurantes')

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
        st.header('Overall Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )

        with col1:
            entregadores_unicos = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric( '# Entregadores', entregadores_unicos )

        with col2:
            avg_distance = distance( df1, fig=False )
            col2.metric( '# Distância media',  avg_distance )
                        
        with col3:
            df_aux = festival( df1, 'Yes', 'avg_time')
            col3.metric( '# Entrega Festival', df_aux )

        with col4:
            df_aux = festival( df1, 'Yes', 'std_time')
            col4.metric( '# STD Festival', df_aux )
        
        with col5:
            df_aux = festival( df1, 'No', 'avg_time')
            col5.metric( 'Entrega s/ Festival', df_aux )

        with col6:
            df_aux = festival( df1, 'No', 'std_time')
            col6.metric( '# STD s/ Festival', df_aux )

    with st.container():
        st.markdown("""___""")
        st.title('Tempo médio de entrega por cidade')
        
        fig = distance( df1, fig=True )
        st.plotly_chart(fig) 

    with st.container():
        st.markdown("""___""")
        st.title('Tempo médio de Entrega por Cidade e por Trânsito')
        fig = avg_std_time_on_traffic( df1 )
        st.plotly_chart(fig)
        
        
    with st.container():
        st.markdown("""___""")
        st.header('Distribuição da Distância')
        df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        st.dataframe( df_aux )

    with st.container():
        st.markdown("""___""")
        st.header('Desvio padrão de Entrega por Cidade')
        df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        fig = go.Figure()
        fig.add_trace( go.Bar( name='Control',
                              x=df_aux['City'],
                              y=df_aux['avg_time'],
                              error_y=dict( type='data', array=df_aux['std_time'])))
        fig.update_layout(barmode='group')
        st.plotly_chart( fig )

