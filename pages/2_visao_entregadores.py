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

# Bibliotecas necessárias
from PIL import Image
from streamlit_folium import folium_static
from haversine import haversine


#Configurando página para exibição em conjunto com a HOME no Streamlit
st.set_page_config(page_title='Visão Entregadores', page_icon='', layout='wide')

#=====================================
# Funções
#=====================================

def top_deliveres (df1, top_asc):
    """ Esta função tem a responsabilidade filtrar os 10 entregadores mais rápidos ou os 10 mais lentos agrupados por cidade
        
        Etapas:
        1. Selecionar as colunas de interesse, agrupar por cidade e por ID do entregador o MENOR tempo deste entregador
        2. Nos parâmetros de entrada, defino se quero os mais rápidos ou mais lentos através da definção do parâmentro top_asc
        3. top_asc = False para os entregadores MAIS RÁPIDOS
        4. top_asc = True para os entregadores MAIS LENTOS
        
        Input: Dataframe e tipo de ordenação
        Output: Dataframe
    """
            
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Delivery_person_ID', 'City']]
                 .groupby(['City', 'Delivery_person_ID'])
                 .min()
                 .sort_values(['City','Time_taken(min)'], ascending = top_asc)
                 .reset_index())

    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

    df2 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)

    return df2



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
# LAYOUT CENTRAL NO STREAMLIT - VISÃO ENTREGADORES
#======================================================
#Título inserido no campo CENTRAL
st.header('Marketplace - Visão Entregadores')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        
        with col1:
            #st.markdown('##### Entregador mais velho')
            mais_velho = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Entregador + velho', mais_velho)
            

        with col2:
            #st.markdown('##### Entregador mais novo')
            mais_novo = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric("Entregador + novo", mais_novo)
            
        with col3:
            #st.markdown('##### Melhor condição de veículo')
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição veículo', melhor_condicao )
            
        with col4:
            #st.markdown('##### Pior condição de veículo')
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição de veículo', pior_condicao )
            
            
    st.markdown('''___''')
          
    with st.container():
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Avaliação média por entregador')
            
            df_aux = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                         .groupby('Delivery_person_ID')
                         .mean()
                         .reset_index())
  
            st.dataframe(df_aux)

            
        with col2:
            st.markdown('#### Avaliação média por trânsito')
            
            df_avg_std_rating_by_traffic = (df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density' ]]
                                               .groupby('Road_traffic_density')
                                               .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Alterando o nome das colunas do DF
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            # Resetando o INDEX

            df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
            
            st.markdown('#### Avaliação média por clima')
            
            df_avg_std_weather = (df1.loc[:, ['Delivery_person_Ratings','Weatherconditions' ]]
                                     .groupby('Weatherconditions')
                                     .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Alterando o nome das colunas do DF
            df_avg_std_weather.columns = ['delivery_mean', 'delivery_std']

            # Resetando o INDEX
            df_avg_std_weather.reset_index()
            st.dataframe(df_avg_std_weather)
            
            
    st.markdown('''___''')
        
    with st.container():
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Top 10 entregadores mais rápidos')
            
            df2 = top_deliveres (df1, top_asc = True)
            st.dataframe(df2)
            
        with col2:
            st.markdown('#### Top 10 entregadores mais lentos')
            
            df2 = top_deliveres (df1, top_asc = False)
            st.dataframe(df2)