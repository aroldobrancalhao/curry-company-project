import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🥡',
    layout='wide'
)


#image_path = '/comunidade_ds/repos/ftc/projeto/'
image = Image.open( 'logo.jpg' )
st.sidebar.image(image, width=180)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fast Delivery in Town')
st.sidebar.markdown("""___""")

st.write("# Curry Company Growth Dashboard")


st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento de Entregadores e Restaurantes
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanis de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semnais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @aroldo
    """)