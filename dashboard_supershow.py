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

# Título Principal
st.title("🚀 Dashboard Super Show | Performance 2025-2026")
st.markdown("---")

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        # 1. Carregar CSV com tratamento de aspas e nomes de colunas
        csv_path = 'SuperShow_25_26.csv'
        if not os.path.exists(csv_path):
            st.error(f"Arquivo não encontrado: {csv_path}")
            return None
            
        df_comp = pd.read_csv(csv_path)
        # Limpar nomes de colunas (remover aspas e espaços)
        df_comp.columns = [str(c).replace('"', '').strip() for c in df_comp.columns]
        
        # 2. Carregar Excel de Metas
        excel_path = 'Projeção e meta 2026.xlsx'
        if not os.path.exists(excel_path):
            st.error(f"Arquivo não encontrado: {excel_path}")
            return None
            
        df_metas_raw = pd.read_excel(excel_path)
        
        # Filtrar apenas lojas SUPER SHOW
        df_metas = df_metas_raw[df_metas_raw['LOJA'].str.contains('SUPER SHOW', na=False, case=False)].copy()
        
        # 3. Padronização para o Join
        def simplify_name(name):
            name = str(name).upper()
            if 'FELIPE' in name: return 'FELIPE CAMARAO'
            if 'GOMES' in name: return 'GOMES ZN'
            return name
        
        # Garantir que as colunas existam antes de aplicar
        if 'NOME_LOJA' in df_comp.columns:
            df_comp['JOIN_KEY'] = df_comp['NOME_LOJA'].apply(simplify_name)
        else:
            st.error(f"Coluna 'NOME_LOJA' não encontrada no CSV. Colunas disponíveis: {list(df_comp.columns)}")
            return None
            
        df_metas['JOIN_KEY'] = df_metas['LOJA'].apply(simplify_name)
        
        # 4. Cruzamento de dados
        df_final = pd.merge(df_comp, df_metas[['JOIN_KEY', 'META DE MAIO', 'META DA SEMANA']], on='JOIN_KEY', how='left')
        return df_final
        
    except Exception as e:
        st.error(f"Erro detalhado no processamento: {e}")
        return None

# Carregamento dos dados
df = load_data()

if df is not None:
    # --- Sidebar com Filtros ---
    st.sidebar.header("Filtros")
    
    cidades_disponiveis = df['CIDADE_LOJA'].unique()
    cidades_selecionadas = st.sidebar.multiselect("Filtrar por Cidade", options=cidades_disponiveis, default=cidades_disponiveis)
    
    df_filtered = df[df['CIDADE_LOJA'].isin(cidades_selecionadas)]

    # --- Métricas ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_25 = df_filtered['Valor Ano Anterior'].sum()
    total_26 = df_filtered['Valor Atual'].sum()
    variacao_media = ((total_26 / total_25) - 1) * 100 if total_25 > 0 else 0
    total_meta = df_filtered['META DE MAIO'].sum()
    atingimento = (total_26 / total_meta) * 100 if total_meta > 0 else 0

    col1.metric("Venda Total 2025", f"R$ {total_25:,.2f}")
    col2.metric("Venda Total 2026", f"R$ {total_26:,.2f}", f"{variacao_media:+.2f}%")
    col3.metric("Meta de Maio", f"R$ {total_meta:,.2f}")
    col4.metric("Atingimento Meta", f"{atingimento:.1f}%")

    st.markdown("---")

    # --- Gráficos ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 Comparativo: 2025 vs 2026")
        df_melted = df_filtered.melt(id_vars=['NOME_LOJA'], value_vars=['Valor Ano Anterior', 'Valor Atual'], 
                           var_name='Ano', value_name='Valor')
        df_melted['Ano'] = df_melted['Ano'].replace({'Valor Ano Anterior': '2025', 'Valor Atual': '2026'})
        fig = px.bar(df_melted, x='NOME_LOJA', y='Valor', color='Ano', barmode='group', text_auto='.2s')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🎯 Realizado vs Meta (Maio 2026)")
        fig_meta = go.Figure()
        fig_meta.add_trace(go.Bar(name='Realizado', x=df_filtered['NOME_LOJA'], y=df_filtered['Valor Atual'], marker_color='royalblue'))
        fig_meta.add_trace(go.Bar(name='Meta', x=df_filtered['NOME_LOJA'], y=df_filtered['META DE MAIO'], marker_color='lightgray'))
        st.plotly_chart(fig_meta, use_container_width=True)

    # --- Tabela ---
    st.markdown("### 📝 Detalhamento por Unidade")
    st.dataframe(df_filtered[['NOME_LOJA', 'CIDADE_LOJA', 'Valor Ano Anterior', 'Valor Atual', 'Variacao (%)', 'META DE MAIO']].style.format({
        'Valor Ano Anterior': 'R$ {:,.2f}',
        'Valor Atual': 'R$ {:,.2f}',
        'Variacao (%)': '{:+.2f}%',
        'META DE MAIO': 'R$ {:,.2f}'
    }), use_container_width=True)

else:
    st.warning("Aguardando carregamento correto dos arquivos...")
