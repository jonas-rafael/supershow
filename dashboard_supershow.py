import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard Super Show 2025-2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Título Principal
st.title("🚀 Dashboard Super Show | Performance 2025-2026")
st.markdown("---")

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        # Dados Comparativos 25/26
        df_comp = pd.read_csv('SuperShow.csv')
        
        # Dados de Metas (Excel)
        df_metas_raw = pd.read_excel('Projeção e meta 2026.xlsx')
        df_metas = df_metas_raw[df_metas_raw['LOJA'].str.contains('SUPER SHOW', na=False, case=False)].copy()
        
        # Padronização de nomes para join (simplificada)
        def simplify_name(name):
            name = str(name).upper()
            if 'FELIPE' in name: return 'FELIPE CAMARAO'
            if 'GOMES' in name: return 'GOMES ZN'
            return name
        
        df_comp['JOIN_KEY'] = df_comp['NOME_LOJA'].apply(simplify_name)
        df_metas['JOIN_KEY'] = df_metas['LOJA'].apply(simplify_name)
        
        # Merge para consolidar
        df_final = pd.merge(df_comp, df_metas[['JOIN_KEY', 'META DE MAIO', 'META DA SEMANA']], on='JOIN_KEY', how='left')
        return df_final
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        return None

# Carregamento dos dados
df = load_data()

if df is not None:
    # --- Sidebar com Filtros ---
    st.sidebar.image("https://via.placeholder.com/150x50.png?text=LOGO+SUPERSHOW", width="stretch")
    st.sidebar.header("Filtros")
    
    # Filtro de Cidade
    cidades_disponiveis = df['CIDADE_LOJA'].unique()
    cidades_selecionadas = st.sidebar.multiselect("Filtrar por Cidade", options=cidades_disponiveis, default=cidades_disponiveis)
    
    # Aplicar Filtros
    df_filtered = df[df['CIDADE_LOJA'].isin(cidades_selecionadas)]

    # --- Seção de Métricas Principais ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_25 = df_filtered['Valor Ano Anterior'].sum()
    total_26 = df_filtered['Valor Atual'].sum()
    variacao_media = ((total_26 / total_25) - 1) * 100 if total_25 > 0 else 0
    total_meta = df_filtered['META DE MAIO'].sum()
    atingimento = (total_26 / total_meta) * 100 if total_meta > 0 else 0

    with col1:
        st.metric("Venda Total 2025", f"R$ {total_25:,.2f}")
    with col2:
        st.metric("Venda Total 2026", f"R$ {total_26:,.2f}", f"{variacao_media:+.2f}%")
    with col3:
        st.metric("Meta de Maio", f"R$ {total_meta:,.2f}")
    with col4:
        st.metric("Atingimento Meta", f"{atingimento:.1f}%")

    st.markdown("---")

    # --- Gráficos ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Comparativo: 2025 vs 2026")
        
        # Transformando para formato longo para o Plotly
        df_melted = df_filtered.melt(id_vars=['NOME_LOJA'], value_vars=['Valor Ano Anterior', 'Valor Atual'], 
                           var_name='Ano', value_name='Valor')
        df_melted['Ano'] = df_melted['Ano'].replace({'Valor Ano Anterior': '2025', 'Valor Atual': '2026'})
        
        fig_comp = px.bar(df_melted, x='NOME_LOJA', y='Valor', color='Ano', barmode='group',
                          text_auto='.2s', color_discrete_sequence=['#636EFA', '#EF553B'],
                          labels={'Valor': 'Faturamento (R$)', 'NOME_LOJA': 'Loja'})
        fig_comp.update_layout(legend_title_text='Ano')
        st.plotly_chart(fig_comp, width="stretch")

    with col_right:
        st.subheader("🎯 Realizado vs Meta (Maio 2026)")
        
        fig_meta = go.Figure()
        
        fig_meta.add_trace(go.Bar(
            name='Realizado',
            x=df_filtered['NOME_LOJA'], y=df_filtered['Valor Atual'],
            marker_color='royalblue',
            text=df_filtered['Valor Atual'].apply(lambda x: f"R$ {x:,.0f}"),
            textposition='auto'
        ))
        
        fig_meta.add_trace(go.Bar(
            name='Meta',
            x=df_filtered['NOME_LOJA'], y=df_filtered['META DE MAIO'],
            marker_color='lightgray',
            text=df_filtered['META DE MAIO'].apply(lambda x: f"R$ {x:,.0f}"),
            textposition='auto'
        ))
        
        fig_meta.update_layout(barmode='group', xaxis_title='Loja', yaxis_title='Valor (R$)')
        st.plotly_chart(fig_meta, width="stretch")

    # --- Tabela de Detalhes ---
    st.markdown("### 📝 Detalhamento por Unidade")
    
    # Formatando a tabela para exibição
    df_display = df_filtered[['NOME_LOJA', 'CIDADE_LOJA', 'Valor Ano Anterior', 'Valor Atual', 'Variacao (%)', 'META DE MAIO']].copy()
    df_display.columns = ['Loja', 'Cidade', 'Faturamento 2025', 'Faturamento 2026', 'Variação (%)', 'Meta Maio']
    
    st.dataframe(df_display.style.format({
        'Faturamento 2025': 'R$ {:,.2f}',
        'Faturamento 2026': 'R$ {:,.2f}',
        'Variação (%)': '{:+.2f}%',
        'Meta Maio': 'R$ {:,.2f}'
    }), width="stretch")

    # --- Insights ---
    st.info("""
    **Insights Rápidos:**
    - Ambas as lojas apresentam variação negativa em relação ao ano anterior no período consolidado.
    - O atingimento da meta de maio está em análise.
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.write("Dashboard gerado em 02/06/2026")

else:
    st.error("Não foi possível carregar os dados. Verifique se os arquivos 'SuperShow_25_26.csv' e 'Projeção e meta 2026.xlsx' estão no diretório.")
    st.info("O erro pode ter ocorrido por falta dos arquivos ou colunas divergentes.")
