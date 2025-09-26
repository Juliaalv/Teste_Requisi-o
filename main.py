import streamlit as st
from datetime import datetime
from config.page_config import configure_page
from utils.data_loader import load_data
from utils.data_processor import prepare_data_with_real_status
from components.sidebar import create_sidebar_filters
from components.kanban import create_kanban_view
from components.analytics import create_analytics
from components.footer import create_footer

def main():
    """Função principal da aplicação com upload obrigatório"""
    # Configurar página
    configure_page()
    
    # Título principal
    st.markdown('<h1 class="main-header">📊 Análise Semanal dos Chamados</h1>', 
               unsafe_allow_html=True)
    
    # Container principal com margem para o rodapé
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # NOVA LÓGICA: Verificar se os dados já estão carregados
    if not _check_data_loaded():
        # Se não há dados carregados, mostrar interface de upload
        _show_upload_interface()
        return  # Para aqui até os dados serem carregados
    
    # Se chegou aqui, os dados estão disponíveis
    with st.spinner("⚙️ Carregando dados do sistema..."):
        df = load_data()
    
    if df is None:
        st.error("❌ Erro ao carregar os dados processados")
        if st.button("🔄 Recarregar dados"):
            _clear_data_cache()
            st.rerun()
        return
    
    # Preparar dados
    with st.spinner("⚙️ Preparando análise com base na Data Alvo..."):
        df = prepare_data_with_real_status(df)
    
    # Verificar se temos dados de DATA_ALVO
    if len(df) == 0:
        st.error("❌ Nenhum dado válido encontrado!")
        st.warning("Verifique se a coluna 'DATA_ALVO' existe e contém datas válidas.")
        return
    
    st.success(f"✅ Sistema carregado! {len(df):,} chamados.")
    
    # Criar filtros
    filtros = create_sidebar_filters(df)
    if filtros[0] is None or filtros[1] is None:
        st.warning("⚠️ Dados insuficientes para análise.")
        return
    
    ano, semana, responsavel, status_filtrados = filtros
    
    # Visualizações principais
    create_kanban_view(df, ano, semana, responsavel, status_filtrados)
    create_analytics(df, ano, semana, responsavel, status_filtrados)
    
    # Informações do sistema na sidebar
    _show_system_info(df, ano, semana, responsavel, status_filtrados)
    
    # Botão para recarregar dados na sidebar
    _show_data_management_sidebar()
    
    # Fechar container principal
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Criar rodapé
    create_footer()

def _check_data_loaded():
    """Verifica se os dados já foram carregados e processados"""
    # Verifica se há dados em cache ou arquivo processado
    if 'data_processed' in st.session_state and st.session_state.data_processed:
        return True
    
    # Verifica se existe arquivo parquet processado
    import os
    if os.path.exists("requisicoes_data.parquet"):
        st.session_state.data_processed = True
        return True
    
    return False

def _show_upload_interface():
    """Mostra interface de upload obrigatório"""
    st.markdown("---")
    st.subheader("📁 Upload dos Arquivos Necessários")
    st.info("Para utilizar o sistema, é necessário fazer upload dos dois arquivos Excel abaixo:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Arquivo 1")
        uploaded_req = st.file_uploader(
            "Relatório de Requisições.xlsx",
            type=['xlsx'],
            help="Arquivo principal com dados das requisições",
            key="upload_req"
        )
        
        if uploaded_req is not None:
            st.success("✅ Arquivo 1 carregado")
            st.caption(f"Tamanho: {uploaded_req.size / 1024:.1f} KB")
    
    with col2:
        st.markdown("### 📄 Arquivo 2")
        uploaded_minha = st.file_uploader(
            "Requisições da Minha Equipe.xlsx", 
            type=['xlsx'],
            help="Arquivo complementar da equipe",
            key="upload_minha"
        )
        
        if uploaded_minha is not None:
            st.success("✅ Arquivo 2 carregado")
            st.caption(f"Tamanho: {uploaded_minha.size / 1024:.1f} KB")
    
    # Botão de processamento
    if uploaded_req is not None and uploaded_minha is not None:
        st.markdown("---")
        col_center = st.columns([1, 2, 1])[1]
        
        with col_center:
            if st.button("🚀 Processar Dados e Iniciar Análise", 
                        type="primary", use_container_width=True):
                _process_uploaded_files(uploaded_req, uploaded_minha)
    
    elif uploaded_req is not None or uploaded_minha is not None:
        st.warning("⚠️ Por favor, faça upload dos dois arquivos para continuar.")
    
    # Informações adicionais
    with st.expander("ℹ️ Informações sobre os arquivos"):
        st.markdown("""
        **Arquivo 1 - Relatório de Requisições.xlsx:**
        - Contém dados principais dos chamados
        - Deve ter colunas: NUM_CHAMADO, DATA_ABERTURA, STATUS, etc.
        
        **Arquivo 2 - Requisições da Minha Equipe.xlsx:**
        - Contém dados complementares da equipe
        - Deve ter colunas: Requisição de Serviço, Data Esperada, etc.
        
        **Processamento:**
        - Os arquivos são mesclados automaticamente
        - Dados são salvos localmente para próximas sessões
        - Formato otimizado para melhor performance
        """)

def _process_uploaded_files(uploaded_req, uploaded_minha):
    """Processa os arquivos enviados"""
    try:
        with st.spinner("🔄 Processando arquivos... Isso pode levar alguns segundos."):
            import pandas as pd
            
            # Carregar dados dos uploads
            df_req = pd.read_excel(uploaded_req)
            df_req_minha = pd.read_excel(uploaded_minha)
            
            # Aplicar processamento original
            df_final = _process_data_original_logic(df_req, df_req_minha)
            
            # Salvar parquet para próximas execuções
            df_final.to_parquet("requisicoes_data.parquet", index=False)
            
            # Marcar como processado
            st.session_state.data_processed = True
            
            st.success("✅ Dados processados com sucesso!")
            st.balloons()
            
            # Recarregar a página para mostrar o dashboard
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivos: {str(e)}")
        st.error("Verifique se os arquivos estão no formato correto e tente novamente.")

def _process_data_original_logic(df_req, df_req_minha):
    """Aplica a lógica original de processamento dos dados"""
    # Filtrar por RESOLVEDOR_PADRAO
    df_req = df_req[df_req['RESOLVEDOR_PADRAO'] == 'AUTOMAÇÃO TELECOM']
    
    # Selecionar colunas do df_req 
    df_req = df_req[['NUM_CHAMADO', 'DATA_ABERTURA', 'DATA_PREV_SOLUCAO',
                     'DATA_QUEBRA_SLA', 'SLA_VIOLADO', 'DATA_RESOLUCAO',
                     'DATA_FECHAMENTO', 'Status', 'TITULO', 'SOLICITANTE', 'RESPONSAVEL']]
    
    # Selecionar colunas do df_req_minha 
    df_req_minha = df_req_minha[['Requisição de Serviço','Data Esperada', 'Resumo', 
                                 'Status', 'Proprietário', 'Cliente', 'Criado em', 
                                 'Resolvido em', 'SLA - Data Prevista Solução']]
    
    # Renomear colunas 
    df_req_minha.rename(columns={'Requisição de Serviço': 'NUM_CHAMADO',
                                 'Resumo': 'TITULO',
                                 'Proprietário': 'RESPONSAVEL',
                                 'Cliente': 'SOLICITANTE',
                                 'Resolvido em': 'DATA_RESOLUCAO',
                                 'Criado em': 'DATA_ABERTURA',
                                 'SLA - Data Prevista Solução': 'DATA_PREV_SOLUCAO',
                                 }, inplace=True)
    
    # Identificar colunas novas 
    colunas_df_req = set(df_req.columns)
    colunas_df_req_minha = set(df_req_minha.columns)
    colunas_novas = colunas_df_req_minha - colunas_df_req
    
    # Fazer o merge 
    colunas_para_merge = ['NUM_CHAMADO'] + list(colunas_novas)
    df_req_minha_filtrado = df_req_minha[colunas_para_merge]
    df_final = pd.merge(df_req, df_req_minha_filtrado, on='NUM_CHAMADO', how='left')
    
    # Tratar colunas nulas
    df_final['RESPONSAVEL'] = df_final['RESPONSAVEL'].fillna('Proprietário Vazio')
    
    # Criar DATA_ALVO 
    df_final['DATA_ALVO'] = df_final['Data Esperada'].fillna(df_final['DATA_PREV_SOLUCAO'])
    
    # Aplicar padronização de colunas
    df_final = _apply_column_mapping(df_final)
    
    return df_final

def _apply_column_mapping(df):
    """Aplica mapeamento de colunas para padronizar nomes"""
    column_mapping = {
        'NUM_CHAMADO': 'REQUISICAO',
        'DATA_ABERTURA': 'DATA_ABERTURA',
        'DATA_ALVO': 'DATA_ALVO', 
        'SLA_VIOLADO': 'SLA_VIOLADO',
        'DATA_RESOLUCAO': 'DATA_RESOLUCAO',
        'Status': 'STATUS',
        'RESPONSAVEL': 'RESPONSAVEL',
        'TITULO': 'RESUMO',
        'SOLICITANTE': 'SOLICITANTE'
    }
    
    # Aplicar mapeamento apenas para colunas existentes
    existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
    df = df.rename(columns=existing_columns)
    return df

def _show_data_management_sidebar():
    """Mostra opções de gerenciamento de dados na sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Gerenciar Dados")
    
    if st.sidebar.button("🗑️ Limpar dados e recarregar"):
        _clear_data_cache()
        st.rerun()
    
    st.sidebar.caption("Use para carregar novos arquivos")

def _clear_data_cache():
    """Limpa cache de dados"""
    import os
    if 'data_processed' in st.session_state:
        del st.session_state.data_processed
    
    # Remover arquivo parquet se existir
    if os.path.exists("requisicoes_data.parquet"):
        os.remove("requisicoes_data.parquet")
    
    # Limpar cache do streamlit
    st.cache_data.clear()

def _show_system_info(df, ano, semana, responsavel, status_filtrados):
    """Mostra informações do sistema na sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Informações do Sistema")
    st.sidebar.caption(f"Data atual: {datetime.now().strftime('%d/%m/%Y')}")
    st.sidebar.caption(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")
    
    # Intervalo de datas dos dados
    data_min = df['DATA_ALVO'].min().strftime('%d/%m/%Y')
    data_max = df['DATA_ALVO'].max().strftime('%d/%m/%Y')
    st.sidebar.caption(f"Período: {data_min} - {data_max}")
    
    # Estatísticas dos filtros
    df_total = df[
        (df['ANO_ALVO'] == ano) & 
        (df['SEMANA_ALVO'] == semana)
    ]
    
    if responsavel != 'Todos':
        df_total = df_total[df_total['RESPONSAVEL'] == responsavel]
    
    if status_filtrados != 'Todos':
        df_filtrado = df_total[df_total['STATUS'].isin(status_filtrados)]
        st.sidebar.caption(f"Registros filtrados: {len(df_filtrado):,} de {len(df_total):,}")
        if len(df_total) > 0:
            percentual = (len(df_filtrado) / len(df_total)) * 100
            st.sidebar.caption(f"Percentual exibido: {percentual:.1f}%")
    else:
        st.sidebar.caption(f"Total de registros: {len(df_total):,}")

if __name__ == "__main__":
    main()