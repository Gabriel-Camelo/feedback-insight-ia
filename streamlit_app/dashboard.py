import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob

# Configuração da página
st.set_page_config(page_title="Feedback Insights Pro", layout="wide", page_icon="📊")
st.title("📈 Painel de Análise de Feedbacks")

# URL da API FastAPI
API_URL = "http://localhost:8000"

# Sidebar para filtros avançados
with st.sidebar:
    st.header("🔍 Filtros Avançados")
    
    # Filtro por período
    min_date = datetime(2023, 1, 1).date()
    max_date = datetime.now().date()
    date_range = st.date_input(
        "Período de análise",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro por sentimento
    sentiment_filter = st.selectbox(
        "Filtrar por sentimento",
        ["Todos", "Positivo", "Neutro", "Negativo"],
        index=0
    )
    
    # Filtro por rótulo
    @st.cache_data
    def get_labels():
        response = requests.get(f"{API_URL}/labels/")
        return [label['name'] for label in response.json()] if response.ok else []
    
    available_labels = get_labels()
    label_filter = st.multiselect(
        "Filtrar por rótulos",
        options=available_labels,
        default=available_labels,
    )

    # Botão para atualizar dados
    refresh_data = st.button("Atualizar Dados")

# Obter dados da API com cache
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_feedbacks():
    response = requests.get(f"{API_URL}/feedbacks/")
    return response.json() if response.ok else []

@st.cache_data(ttl=300)
def get_purchases():
    response = requests.get(f"{API_URL}/purchases/")
    return response.json() if response.ok else []

# Processamento dos dados
feedbacks = get_feedbacks()
purchases = get_purchases()

if not feedbacks:
    st.warning("⚠️ Nenhum feedback encontrado na base de dados.")
    st.stop()

# Criar DataFrame e aplicar filtros
df_feedbacks = pd.DataFrame(feedbacks)

# Converter datas e filtrar por período
df_feedbacks['created_at'] = pd.to_datetime(df_feedbacks['created_at'])
if len(date_range) == 2:
    mask = (df_feedbacks['created_at'].dt.date >= date_range[0]) & \
           (df_feedbacks['created_at'].dt.date <= date_range[1])
    df_feedbacks = df_feedbacks.loc[mask]

# Filtro por sentimento
if sentiment_filter != "Todos":
    df_feedbacks = df_feedbacks[df_feedbacks["sentiment_label"] == sentiment_filter]

# Filtro por rótulos
if label_filter:
    feedbacks_with_labels = []
    for feedback in feedbacks:
        feedback_labels = [fl['label']['name'] for fl in feedback.get('labels', []) if 'label' in fl]
        if any(label in feedback_labels for label in label_filter):
            feedbacks_with_labels.append(feedback)
    df_feedbacks = pd.DataFrame(feedbacks_with_labels)

# Layout principal
tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🔍 Análise Detalhada", "📝 Feedbacks Completos"])

with tab1:
    # Métricas de alto nível
    st.subheader("📈 Métricas Chave")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Feedbacks", len(df_feedbacks))
    
    with col2:
        avg_score = df_feedbacks['sentiment_score'].mean()
        st.metric("Média de Sentimento", f"{avg_score:.2f}", 
                 "👍 Positivo" if avg_score > 0.6 else "👎 Negativo" if avg_score < 0.4 else "😐 Neutro")
    
    with col3:
        if df_feedbacks[df_feedbacks['sentiment_label'] == 'Positivo'].shape[0] != 0:
            pos_perc = df_feedbacks[df_feedbacks['sentiment_label'] == 'Positivo'].shape[0] / df_feedbacks.shape[0]
        else:
            pos_perc = 0
        st.metric("Feedbacks Positivos", f"{pos_perc:.1%}")
    
    with col4:
        if df_feedbacks[df_feedbacks['sentiment_label'] == 'Negativo'].shape[0] != 0:
            neg_perc = df_feedbacks[df_feedbacks['sentiment_label'] == 'Negativo'].shape[0] / df_feedbacks.shape[0]
        else:
            neg_perc = 0
        st.metric("Feedbacks Negativos", f"{neg_perc:.1%}")
    
    # Gráficos principais
    st.subheader("📊 Distribuição de Sentimentos")
    fig1 = px.pie(
        df_feedbacks,
        names="sentiment_label",
        color="sentiment_label",
        color_discrete_map={'Positivo':'green', 'Neutro':'gray', 'Negativo':'red'},
        hole=0.4
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Evolução temporal
    if len(df_feedbacks) > 0:
        st.subheader("📅 Tendência Temporal")
        
        # Garantir que a coluna é datetime e converter para timezone-naive se necessário
        df_feedbacks['created_at'] = pd.to_datetime(df_feedbacks['created_at']).dt.tz_localize(None)
        
        try:
            # Criar cópia para não modificar o DataFrame original
            df_temp = df_feedbacks.copy()
            df_temp = df_temp.set_index('created_at')
            
            # Verificar se o índice é datetime
            if isinstance(df_temp.index, pd.DatetimeIndex):
                df_temporal = df_temp['sentiment_score'].resample('W').mean().reset_index()
                
                fig2 = px.line(
                    df_temporal,
                    x='created_at',
                    y='sentiment_score',
                    title="Evolução do Sentimento Médio (Semanal)"
                )
                fig2.add_hline(y=0.5, line_dash="dash", line_color="red")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Os dados de data não estão no formato correto para análise temporal.")
        except Exception as e:
            st.error(f"Erro ao gerar gráfico temporal: {str(e)}")
    else:
        st.warning("Nenhum dado disponível para mostrar a tendência temporal.")

with tab2:
    # Análise de tópicos
    st.subheader("🏷️ Análise por Rótulos")
    
    # Processar rótulos
    all_labels = []
    for feedback in feedbacks:
        for feedback_label in feedback.get('labels', []):
            if 'label' in feedback_label:
                all_labels.append(feedback_label['label']['name'])
    
    if all_labels:
        df_labels = pd.DataFrame(all_labels, columns=['label'])
        label_counts = df_labels['label'].value_counts().reset_index()
        label_counts.columns = ['label', 'count']
        
        fig3 = px.bar(
            label_counts.head(10),
            x='label',
            y='count',
            color='count',
            title="Top 10 Rótulos Mais Frequentes"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Word Cloud
        st.subheader("☁️ Nuvem de Palavras dos Rótulos")
        text = ' '.join(all_labels)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig_wc, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig_wc)
    else:
        st.warning("Nenhum rótulo encontrado nos feedbacks.")
    
    # Análise de correlação
    st.subheader("🔗 Correlação entre Sentimento e Produtos")
    if purchases and 'purchase_id' in df_feedbacks.columns:
        df_purchases = pd.DataFrame(purchases)
        df_merged = pd.merge(df_feedbacks, df_purchases, left_on='purchase_id', right_on='id')
        
        fig4 = px.box(
            df_merged,
            x='product_name',
            y='sentiment_score',
            color='sentiment_label',
            title="Distribuição de Sentimento por Produto"
        )
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    # Tabela interativa de feedbacks
    st.subheader("📝 Feedbacks Detalhados")
    
    # Adicionar análise de polaridade do TextBlob
    df_feedbacks['polarity'] = df_feedbacks['comment'].apply(lambda x: TextBlob(x).sentiment.polarity)
    
    # Mostrar tabela com filtros
    cols_to_show = st.multiselect(
        "Colunas para exibir",
        options=df_feedbacks.columns,
        default=['comment', 'sentiment_label', 'sentiment_score', 'created_at']
    )
    
    st.dataframe(
        df_feedbacks[cols_to_show],
        height=600,
        use_container_width=True,
        column_config={
            "comment": "Comentário",
            "sentiment_label": "Sentimento",
            "sentiment_score": "Score",
            "created_at": "Data"
        }
    )

# Rodapé
st.markdown("---")
st.caption("📌 Painel de Análise de Feedbacks - v1.0 | Atualizado em " + datetime.now().strftime("%d/%m/%Y %H:%M"))