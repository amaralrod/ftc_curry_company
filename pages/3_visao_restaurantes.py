#========================================
# Importando bibliotecas
#========================================

#Libraries
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
import re
import numpy as np

# Bibliotecas necessárias
from PIL import Image
from streamlit_folium import folium_static
from haversine import haversine


#Configurando página para exibição em conjunto com a HOME no Streamlit
st.set_page_config(page_title='Visão Entregadores', page_icon='', layout='wide')


#=====================================
# Funções
#=====================================

def avg_time_city_traffic (df1):
    """ Esta função calcula o tempo médio oe o desvio-padrão do tempo de entrega agrupado por cidade e por tipo de tráfego
        
        Operações:
        1. Definição das colunas de interesse
        2. Agrupar por cidade e por tráfego
        3. Calcular o tempo médio e o desvio padrão
        4. Plotar o gráfico sunburst
        
        Input: Dataframe
        Output: Figura Sunburst
    """
    
    df_mean_std_time = df1.loc[:,['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
    df_mean_std_time.columns = ['City', 'Road_traffic_density', 'avg_time', 'std_time']
    #df_mean_std_time

    fig = px.sunburst(df_mean_std_time, path=['City', 'Road_traffic_density'], values = 'avg_time', color = 'std_time', color_continuous_scale = 'RdBu', color_continuous_midpoint = np.average(df_mean_std_time['std_time']))
    
    return fig





def avg_std_time_delivery (df1, festival, op):
    """ Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df1: Dataframe com os dados necessários para o cálculo
                -festival:
                    'Yes': Período de Festival
                    'No': Período sem Festival
                - op: Tipo de operação que precisa ser calculado:
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo
   
            Output:
                - df_aux: Dataframe com 2 colunas e 1 linha
    """
                
    df_mean_std_time = df1.loc[:,['Time_taken(min)','Festival']].groupby('Festival').agg({'Time_taken(min)':['mean','std']}).reset_index()
    df_mean_std_time.columns = ['Festival', 'avg_time', 'std_time']
    #df_mean_std_time

    linhas_selecionadas = df_mean_std_time['Festival'] == festival
    df_aux = df_mean_std_time.loc[linhas_selecionadas, op]
    df_aux = np.round(df_aux.mean(), 2)    #importante esta etapa para arredondar para duas casas decimais

    return df_aux



def distance (df1, fig):
    """ Esta função de calcular a distância entre dois pontos utilizando a metodologia HAVERSINE
        
        Operações:
        1. Definição das colunas de interesse
        2. Aplicar a função lambda às colunas que indicam LAT e LONG dos restaurantes e medindo a distância em relação aos pontos de LAT e LONG dos pontos de entrega
        3. Calcular a distÂncia média  e arredondar para duas casas decimais
        
        Input: Dataframe
        Output: Dataframe
    """
    if fig == False:       
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( 
                                                       (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                       (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)

        df1_avg_dist = np.round(df1['distance'].mean(), 2)  #importante esta etapa para arredondar para duas casas decimais

        return df1_avg_dist
    
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['distance'] = df1.loc[:, cols].apply(lambda x:haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)

        avg_dist = df1.loc[:,['distance', 'City']].groupby('City').mean().reset_index()
        avg_dist.columns = ['City', 'mean_dist']
        fig = go.Figure(data = [go.Pie(labels = avg_dist['City'], values = avg_dist['mean_dist'], pull=[0,0.1,0])])
        
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

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## FASTEST DELIVERY IN TOWN')
st.sidebar.markdown( """---""")

st.sidebar.markdown('## Selecione a janela de data desejada:')

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

## Inserindo um RODAPé na BARRA LATERAL
st.sidebar.markdown('##### Powered by Comunidade DS')
st.sidebar.markdown('###### email: amaralrodrigo@hotmail.com')



#======================================================
# LAYOUT CENTRAL NO STREAMLIT - VISÃO RESTAURANTES
#======================================================

#Título inserido no campo CENTRAL
st.header('Marketplace - Visão Restaurantes')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():

        col1, col2, col3, col4, col5, col6 = st.columns(6)
    
        with col1:
            #st.markdown('###### Qnt Entregadores')
            qtd_entregadores = df1.loc[:, 'Delivery_person_ID'].nunique()
            
            col1.metric('Qtd entregadores', qtd_entregadores)

            
        with col2:
            #st.markdown('###### Distância média')
            df1_avg_dist = distance (df1, fig=False)
            
            col2.metric('Dist média entrega', df1_avg_dist)

            
        with col3:
            #st.markdown('###### Tempo de entrega médio COM Festival')
            df_aux = avg_std_time_delivery (df1, 'Yes', 'avg_time')
           
            col3.metric('Tempo médio entrega FESTIVAL', df_aux)

            
        with col4:
            #st.markdown('###### Desvio padrão do tempo médio das entregas COM Festival')
            df_aux = avg_std_time_delivery (df1, 'Yes', 'std_time')
                
            col4.metric('Std tempo entregas (FESTIVAL)', df_aux)

        with col5:
            #st.markdown('###### Tempo de entrega médio COM Festival')
            df_aux = avg_std_time_delivery (df1, 'No', 'avg_time')
                
            col5.metric('Tempo médio entrega S/FESTIVAL', df_aux)

            
        with col6:
            #st.markdown('###### Desvio padrão do tempo médio das entregas COM Festival')
            df_aux = avg_std_time_delivery (df1, 'No', 'std_time')
            
            col6.metric('Std tempo entregas (S/FESTIVAL)', df_aux)
            
            

    st.markdown('''---''')
  
    with st.container():
        
        col1, col2 = st.columns(2)
  
        with col1:
            st.markdown('#### Distribuição do tempo por cidade')
            
            df_mean_std_time = df1.loc[:,['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_mean_std_time.columns = ['City', 'mean_time', 'std_time']
            #df_mean_std_time
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name = 'Control', x = df_mean_std_time['City'], y = df_mean_std_time['mean_time'], error_y = dict(type = 'data', array = df_mean_std_time['std_time'])))
            fig.update_layout(barmode = 'group')
            
            st.plotly_chart(fig, use_container_width = True)          
            

        with col2:
            st.markdown('#### Tempo médio por cidade, por tipo de entrega')
            
            df_type_mean_std_time = df1.loc[:,['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_type_mean_std_time.columns = ['City', 'Type_of_order', 'mean_time', 'std_time']
            st.dataframe(df_type_mean_std_time, use_container_width = True)

            
    st.markdown('''---''')
    
    with st.container():
        
        col1, col2 = st.columns (2)
        
        with col1:
            st.markdown('#### Distância média por cidade')
            
            fig = distance (df1, fig=True)
            
            st.plotly_chart(fig, use_container_width = True)
        
        
        with col2:
            st.markdown('#### Tempo médio por cidade e tipo de tráfego')
                      
            fig = avg_time_city_traffic (df1)
            
            st.plotly_chart(fig, use_container_width = True)
