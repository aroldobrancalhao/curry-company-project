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

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

# ==================================================== 
# Funções
# ==================================================== 

def country_map( df1 ):
    data_plot = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude' ]].groupby( ['City', 'Road_traffic_density'] ).median().reset_index()
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    folium_static( map_, width=1024 , height=600)
    return None

def orber_share_by_week( df1 ):
    # Quantidade de pedidos por entregador por Semana
    # Quantas entregas na semana / Quantos entregadores únicos por semana
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig

def orber_by_week( df1 ):
    # Quantidade de pedidos por Semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    # gráfico
    px.bar( df_aux, x='week_of_year', y='ID' )
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig

def traffic_order_city( df1 ):
    cols = ['ID', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_metric( df1 ):
    # Quantidade de pedidos por dia
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date'    ).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']       
    # gráfico
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
    
    return fig

def traffic_order_share( df1 ):               
    cols = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN ', :]
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    
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
image = Image.open( 'teste.jpg' )
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

tab1, tab2, tab3  =st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1: 
    with st.container():
        fig = order_metric( df1 )
        st.markdown( '# Orders by Day' )
        st.plotly_chart( fig, use_container_width=True )
          
    with st.container(): 
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share( df1 )
            st.header( 'Traffic Order Share' )
            st.plotly_chart( fig, use_container_width=True )
        
        with col2:
            fig = traffic_order_city( df1 )
            st.header( 'Traffic Order City' )
            st.plotly_chart( fig, use_container_width=True )          
            
with tab2:
    with st.container():
        st.header('Order by Week')
        fig = orber_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )

    with st.container():
        st.header('Order Share by Week')
        fig = orber_share_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )


with tab3:    
    st.header( 'Country Maps' )
    map_ = country_map( df1 )
    

