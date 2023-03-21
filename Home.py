import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home') #st.set_page_config(page_title='Home', page_icon='')

image_path = 'logo.jpg' #'C:\Users\amara\documents\repos\ftc\logo.jpg'
image = Image.open ( image_path )
st.sidebar.image(image, width=220)

#image_path =  'C:\Users\amara\Documents\repos\ftc\'
#image = Image.open (image_path + 'logo.jpg')
#st.sidebar.image (image, width=120)

st.sidebar.markdown( '# Cury Company')
st.sidebar.markdown( '## Fastest Delivery in Town')
st.sidebar.markdown( """___""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento da Empresa, entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão da Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
        
    ### Ask for Help
    - Rodrigo Amaral - amaralrodrigo@hotmail.com
    """)