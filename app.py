import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard UnnieTeste",
    page_icon="💹",
    layout="wide",
)

# --- Carregamento dos dados ---
# Usando cache para não recarregar os dados a cada interação do usuário
@st.cache_data
def carregar_dados():
    df = pd.read_csv("https://raw.githubusercontent.com/UnniecornCatST/teste-para-o-dash/refs/heads/main/treinamento-imersao.csv")
    return df

df = carregar_dados()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ano_de_trabalho'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_da_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano_de_trabalho'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_da_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("💰 Dashboard de Teste de Análise de Dados da Unnie")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# Verifica se há dados após a filtragem. Se não houver, mostra aviso e para.
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop() # Impede que o resto do código seja executado

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

salario_medio = df_filtrado['usd'].mean()
salario_mediano = df_filtrado['usd'].median() # <-- ADICIONADO
salario_maximo = df_filtrado['usd'].max()
total_registros = df_filtrado.shape[0]
cargo_mais_frequente = df_filtrado['cargo'].mode()[0]

# MUDAMOS PARA 5 COLUNAS
col1, col2, col3, col4, col5 = st.columns(5) 

col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário mediano", f"${salario_mediano:,.0f}") # <-- ADICIONADO
col3.metric("Salário máximo", f"${salario_maximo:,.0f}")
col4.metric("Total de registros", f"{total_registros:,}")
col5.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
    grafico_cargos = px.bar(
        top_cargos,
        x='usd',
        y='cargo',
        orientation='h',
        title="Top 10 cargos por salário médio",
        labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
    )
    grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(grafico_cargos, use_container_width=True)

with col_graf2:
    grafico_hist = px.histogram(
        df_filtrado,
        x='usd',
        nbins=30,
        title="Distribuição de salários anuais",
        labels={'usd': 'Faixa salarial (USD)', 'count': 'Quantidade'} # Adicionei um label para 'count'
    )
    st.plotly_chart(grafico_hist, use_container_width=True) # Faltava esta linha para mostrar o gráfico


col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
    remoto_contagem.columns = ['tipo_de_trabalho', 'quantidade']
    grafico_remoto = px.pie(
        remoto_contagem,
        names='tipo_de_trabalho',
        values='quantidade',
        title='Proporção dos tipos de trabalho',
        hole=0.5
    )
    grafico_remoto.update_traces(textinfo='percent+label')
    grafico_remoto.update_layout(title_x=0.1)
    st.plotly_chart(grafico_remoto, use_container_width=True)

with col_graf4:
    # ADICIONAMOS UM FILTRO (SELECTBOX) AQUI
    st.markdown("##### Salário por país para um cargo específico") # Um subtítulo para o filtro
    cargos_disponiveis_mapa = sorted(df_filtrado['cargo'].unique())
    cargo_selecionado_mapa = st.selectbox(
        "Selecione o cargo", 
        cargos_disponiveis_mapa
    )

    # O código abaixo agora usa a variável 'cargo_selecionado_mapa'
    df_mapa = df_filtrado[df_filtrado['cargo'] == cargo_selecionado_mapa]
    
    if not df_mapa.empty:
        media_pais = df_mapa.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_pais,
            locations="residencia_iso3",
            color="usd",
            color_continuous_scale='rdylgn',
            # Título dinâmico com base na seleção
            title=f'Salário Médio de {cargo_selecionado_mapa} por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning(f"Cargo '{cargo_selecionado_mapa}' não encontrado para os filtros selecionados.")


# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados") # CORRIGIDO: Aspas
st.dataframe(df_filtrado) # CORRIGIDO: df_filtrado
