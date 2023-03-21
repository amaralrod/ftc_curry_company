#========================================
# Importando bibliotecas
#========================================
import pandas as pd
import re
#from google.colab import drive

#Importando bibliotecas para traçar gráficos
#pip install plotly #(Ou digitar esse comando SEM ! diretamente no TERMINAL)
import plotly.express as px
import plotly.graph_objects as go

# Importando biblioteca para inserir FOTOS
from PIL import Image

#Importando MAPA
#pip install streamlit-folium #(Ou digitar esse comando SEM ! diretamente no TERMINAL)
import folium
# Importando o mapa pra RODAR NO ###STREAMLIT###
from streamlit_folium import folium_static


# Importando biblioteca que mede distância a partir de longitude e latitude
#pip install haversine
from haversine import haversine

# Importando biblioteca para editar o STREAMLIT
import streamlit as st


#Configurando página para exibição em conjunto com a HOME no Streamlit
st.set_page_config(page_title='Visão Empresa', page_icon='', layout='wide')

#=====================================
# Funções
#=====================================

def country_map (df1):
    """ Esta função tem a responsabilidade de gerar um mapa identificando os pontos de entrega e, adicionalmente, algumas informações relevantes destes pontos
                 
         Etapas:
         1. Definição das váriáveis de interesse e agrupar os dados por cidade e por densidade de tráfego e ponto médio entre latitudes e longitudes
         2. Criação do MAPA utilizado a biblioteca FOLIUM
         3. Marcar um PIN no MAPA criado para cada segregação feita no Groupby
         4. Publicar o MAPA com os PIN apontados
              
        Input: Dataframe
        Output: variável representando o Gráfico de linhas
    """
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'City', 'Road_traffic_density']
    df_aux = (df1.loc[:, cols].groupby(['City','Road_traffic_density']).median().reset_index())

    # Apontando o ponto médio dos pontos de entrega no mapa
    map = folium.Map()

    #folium.Marker([latitude, longitude]).add_to(map)  <--- Esse é o formato dos lançamento dos pontos
    #for i in len(df_aux):
    # folium.Marker( [ df_aux.loc[i, 'Delivery_location_latitude'], df_aux.loc[i,'Delivery_location_longitude'] ] ).add_to(map)

    for index, location_info in df_aux.iterrows():  #interrows() transforma o dataframe num objeto de interação
        folium.Marker( [ location_info['Delivery_location_latitude'], 
                   location_info['Delivery_location_longitude']],
                   popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
        
    folium_static(map, width=1024, height=600)

    return
        
        
    #Definindo quais as váriáveis de interesse e agrupado os dados considerando por cidade e por densidade de tráfego e ponto médio entre latitudes e longitudes
#    df_aux = (df1.loc[:, ['Delivery_location_latitude', 'Delivery_location_longitude', 'City', 'Road_traffic_density']].groupby(['City','Road_traffic_density']).median().reset_index())

    # Apontando o ponto médio dos pontos de entrega no mapa
#    map = folium.Map()

    #folium.Marker([latitude, longitude]).add_to(map)  <--- Esse é o formato dos lançamento dos pontos
    #for i in len(df_aux):
    # folium.Marker( [ df_aux.loc[i, 'Delivery_location_latitude'], df_aux.loc[i,'Delivery_location_longitude'] ] ).add_to(map)

#    for index, location_info in df_aux.iterrows():  #interrows() transforma o dataframe num objeto de interação
#        folium.Marker( [ location_info['Delivery_location_latitude'], 
#                         location_info['Delivery_location_longitude']],
#                         popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

#    folium_static(map, width=1024, height=600)
    
    
#    return none



def orders_week_deliverer (df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de linha referente a quantidade de entregas por semana por entregador
                 
         Etapas:
         1. Criação de dois dataframes. Um agrupando o número de pedidos por semana e o segundo agrupando o número de pedidos por entregador
         2. Realizar a fusão de ambos os dataframes utilizando a função MERGE
         3. Criação de uma coluna relacionando o número de entregas da semana POR entregador (x/y)
         4. Atribuição da variável que será utilizada plotar um gráfico de linha via plotly_express
              
        Input: Dataframe
        Output: variável representando o Gráfico de linhas
    """
    #Quantidade de entregas por semana
    df_aux1 = (df1.loc[:, ['ID', 'week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index())

    #Quantidade de entregadores únicos por semana
    df_aux2 = (df1.loc[:, ['Delivery_person_ID','week_of_year']]
                  .groupby('week_of_year')
                  .nunique()
                  .reset_index())

    #Antes de dividir um pelo outro, preciso uní-los no mesmo DF
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')

    #Criando uma nova coluna executando a operação desejada
    df_aux['orders_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    df_aux

    #Plotando gráfico de linha
    fig = px.line(df_aux, x='week_of_year', y='orders_by_deliver')

    return fig


def orders_week (df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de linha referente ao número de entregas por semana
                 
         Etapas:
         1. Criação da coluna ce dia da semana
         2. Definir colunas de interesse e aplicar a operação de Groupby
         3. PAtribuição da variável que será utilizada para via plotly_express
              
        Input: Dataframe
        Output: variável representando o Gráfico de linhas
    """
        
    #Não possuo coluna com SEM, vou utilizar um comando que transformará os dias em semana
    #Importante não substituir e sim CRIAR uma nova coluna no meu DATAFRAME
    df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U")

    #Selecionando colunas de interesse
    cols = ['ID', 'week_of_year']

    # Agrupando as linhas
    df_aux = (df1.loc[:, cols]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())

    #Definindo o gráfico de LINHA que será desenhado através do plotly_express
    fig = px.line(df_aux, x='week_of_year', y='ID')
    
    return fig


def orders_city_traffic (df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de pizza referente à distribuição número de entregas por tipo de tráfego
                 
        Etapas:
        1. Definir colunas de interesse e aplicar a operação de Groupby
        2. Atribuição da variável que será utilizada para Plotar o gráfico via plotly_express
              
        Input: Dataframe
        Output: Atribuição da variável que será utilizada para plotar Gráfico de pizza utilizando a biblioteca plotly express
    
    """
    
    # Selecionando minhas colunas de interesse
    cols = ['ID','City', 'Road_traffic_density']

    # Aplicando a minha operação sobre o meu DF
    df_aux = (df1.loc[: , cols]
                 .groupby(['City', 'Road_traffic_density'])
                 .count()
                 .reset_index())

    # Desenhando o gráfico de pizza
    fig = px.pie(df_aux, values='ID', names='City')

    return fig


def orders_traffic (df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de pizza referente à distribuição número de entregas por tipo de tráfego
                 
         Etapas:
         1. Definir colunas de interesse e aplicar a operação de Groupby
         2. Atribuição da variável que será utilizada para Plotar o gráfico via plotly_express
              
        Input: Dataframe
        Output: Atribuição da variável que será utilizada para plotar Gráfico de pizza utilizando a biblioteca plotly express
    
    """
    
    #Definindo colunas de interesse
    cols = ['ID', 'Road_traffic_density']

    #Aplicando a minha operação sobre as linhas do DF
    df_aux = (df1.loc[ :, cols]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())

    #Criando coluna com o percentual para ser utilzado no grafico de pizza
    df_aux['percentual_entregas'] = 100*(df_aux['ID']/df_aux['ID'].sum())

    #Desenhando gráfico de pizza
    fig = px.pie( df_aux, values='percentual_entregas', names = 'Road_traffic_density')

    return fig


def orders_day (df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de barras referente ao Número de entregas por dia

        Input: Dataframe
        Output: Gráfico de barras
    """

    #Colunas de interesse
    cols = ['ID', 'Order_Date']

    #Segregação das linhas
    df_aux = (df1.loc[:, cols]
                 .groupby('Order_Date')
                 .count()
                 .reset_index())

    #Renomeando a coluna
    df_aux.columns = ['Order_Date', 'qnt_entregas']

    #Definindo a figura que será desenhada através do plotly_expresse
    fig = px.bar(df_aux, x='Order_Date', y='qnt_entregas')

    return fig


def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe
        
        Tipos de Limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços na variável texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    """
    
    # 1. Convertendo a coluna Age de trexto para número e excluindo linhas "vazias":
    linhas_validas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_validas,:].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2. Convertendo coluna Ratings de texto para numero decimal
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 4.0 Convertendo multiple_deliveries de texto para número inteiro e excluindo valores vazios
    linhas_validas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_validas, :].copy()

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    ## 4.1 Excluindo células vazias no 'Weatherconditions'
    linhas_validas = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[linhas_validas, : ].copy()

    ## 4.2 Excluindo células vazias no 'City'
    linhas_validas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_validas, : ].copy()

    ## 4.3 Excluindo células vazias no 'Festival'
    linhas_validas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_validas, : ].copy()


    # 5. Comando para resetar o INDEX (lembrando que o DROP=TRUE serve para evitar que mantenha o INDEX antigo como coluna 1)
    # Se eu não resetar o INDEX antes do comando FOR dá BUG pq eu removi várias linhas ao longo da limpeza!!!
    df1 = df1.reset_index( drop = True )


    # 3. Convertendo coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )


    # 6. Remover espaco da string (ou object)

    #Forma 01:
    #for i in range( len( df1 ) ):
    #  df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()
    #  df1.loc[i, 'Delivery_person_ID'] = df1.loc[i, 'Delivery_person_ID'].strip()

    #Forma 02:
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 7. Comando para remover o texto de números:

    ## Forma 01:
    #for i in range( len( df1 ) ):
    #  df1.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df1.loc[i, 'Time_taken(min)'] )

    ## Forma 02:
    #df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].split(' ') [1]

    ## Forma 03:
    #df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].replace('(min) ', '')

    ## Forma 04:
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ' )[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)


    #Não possuo coluna com SEM, vou utilizar um comando que transformará os dias em semana
    #Importante não substituir e sim CRIAR uma nova coluna no meu DATAFRAME
    df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U")
    df1['week_of_year'] = df1['week_of_year'].astype(int)
    
    #df1.dtypes
    
    return df1



# ------------------------------------Início da Estrutura lógica do código--------------------------------
#

#=============================
# Importando dataset
#=============================

#Montando o Google Drive como se fosse um PENDRIVE
#drive.mount('/content/drive')
#df_raw = pd.read_csv('/content/drive/MyDrive/FTC - Analise de Dados/train.csv')
#df_raw.head()

#Carregando o arquivo meu DATASET (local)

df_raw = pd.read_csv('dataset/train.csv')
#df_raw.head()

#Criando uma cópia do meu original
df1 = df_raw.copy()

#=============================
#Limpando os dados do DATASET
#=============================
df1 = clean_code(df1)


#=========================================================================
#Configurando para usar toda a largura da página do navegador no STREAMLIT
#=========================================================================
#st.set_page_config(layout="wide") #Quando fui rodar a PAGINA HOME essa etapa foi colocada juntamente com a importação de BIBLIOTECAS


#=======================================================
# LAYOUT  do SIDEBAR
#=======================================================

image_path = 'logo.jpg' #'C:\Users\amara\documents\repos\ftc\ciclo_05\logo.jpg'
image = Image.open ( image_path )
st.sidebar.image(image, width=220)


st.header('Market Place - Visão Empresa')

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## FASTEST DELIVERY IN TOWN')
st.sidebar.markdown( """---""")

st.sidebar.markdown('## Selecione uma janela de data desejada:')

# Inserindo o FILTRO DE DATA no formato SLIDER (date_slider)
data_slider = st.sidebar.slider('Até que valor?', value=pd.datetime(2022, 4, 13), min_value=pd.datetime(2022, 2, 11), max_value=pd.datetime(2022, 4, 6), format='DD-MM-YYYY')

# Criando linha para separação das informação
st.sidebar.markdown( """---""")

# INSERINDO O FILTRO DE TIPOS DE TRÁFEGO do tipo MULTISELECT
traffic_options = st.sidebar.multiselect('Quais as condições de trânsito?',
                                         ['Low', 'Medium', 'High', 'Jam'],
                                         default = ['Low', 'Medium', 'High', 'Jam'])

#IMPLEMENTANDO A FUNCIONALIDADE DOS FILTROS, até então estavam visíveis mas não filtravam os dados
linhas_selecionadas = df1['Order_Date'] <= data_slider
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#Comando apenas para exibir o Dataframe resultante após aplicação dos filtros =D
#st.dataframe(df1)


#======================================================
# LAYOUT CENTRAL NO STREAMLIT
#======================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #1. Quantidade de pedidos por dia. - função orders_day
        st.markdown('# Orders by day')  #ou testar st.header('Orders by day')
        fig = orders_day(df1)
        st.plotly_chart(fig, use_container_width = True) #Exibir no STREAMLIT o gráfico de barras gerado utilizando a biblioteca PLOTLY

    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            #3. Distribuição dos pedidos por tipo de tráfego.
            st.markdown('### Distribuição dos pedidos por tipo de tráfego')
            fig = orders_traffic (df1)
                        
            st.plotly_chart (fig, use_container_width = True)
                       
                        
        with col2:
            #4. Comparação do volume de pedidos por cidade e tipo de tráfego.
            st.markdown('### Volume de pedidos por cidade e tipo de tráfego')
            fig = orders_city_traffic (df1)
            
            st.plotly_chart (fig, use_container_width= True)
      
    
with tab2:
    with st.container():
        #2. Quantidade de pedidos por semana.
        st.markdown('### Quantidade de pedidos por semana')
        fig = orders_week (df1)

        st.plotly_chart(fig, use_container_width = True)     
        
            
    with st.container():
        #5. A quantidade de pedidos por entregador por semana. (Quantidade de pedidos por semana / Quantidade de  entregadores por semana)
        st.markdown('### Quantidade de pedidos por entregador por semana')
        fig = orders_week_deliverer (df1)
        
        st.plotly_chart(fig, use_container_width = True)
            
            
    
with tab3:
    st.markdown('## Distribuição geográfica dos pedidos')
    ## # 6. A localização central de cada cidade por tipo de tráfego
    
    country_map (df1)

    
