import pandas as pd
import streamlit as st
from datetime import datetime

def create_sidebar_filters(df):
    """Cria filtros na sidebar"""
    st.sidebar.header("🔍 Filtros de Análise")
    
    # Informar semana atual
    semana_atual = datetime.now().isocalendar().week
    ano_atual = datetime.now().year
    st.sidebar.info(f"📅 Semana atual: {semana_atual}/{ano_atual}")
    
    # Filtro de período - baseado na DATA_ALVO
    st.sidebar.subheader("📅 Semana do Ano")
    anos = sorted(df['ANO_ALVO'].dropna().unique().tolist())
    if not anos:
        return None, None, None, None
        
    ano_selecionado = st.sidebar.selectbox("Ano:", anos, index=len(anos)-1)
    
    df_ano = df[df['ANO_ALVO'] == ano_selecionado]
    semanas = sorted(df_ano['SEMANA_ALVO'].dropna().unique().tolist())
   # Definir limites e valor inicial
    min_semana = min(semanas)
    max_semana = max(semanas)
    
    # Destacar semana atual se estiver disponível
    if ano_selecionado == ano_atual and semana_atual in semanas:
        valor_inicial = semana_atual
    else:
        # Se a semana atual não estiver disponível, usar a última semana do ano selecionado
        valor_inicial = max_semana

    # 2. Filtro da Semana (Mudado para number_input com setas)
    # Usamos o `value` para definir o valor inicial e `min_value`/`max_value` para limites
    semana_selecionada = st.sidebar.number_input(
        "Semana:", 
        min_value=min_semana, 
        max_value=max_semana, 
        value=valor_inicial,
        step=1,
        key='filtro_semana_number_input'
    )
    semana_selecionada = int(semana_selecionada) if semana_selecionada is not None else valor_inicial
    
    # Filtro de responsável
    responsavel_selecionado = _create_responsavel_filter(df) 
    
    # Filtro de status
    status_selecionados = _create_status_filter(df)
    
    # Filtro de requisição (busca)
    _create_requisicao_filter(df)
    
    # Mostrar resumo dos filtros aplicados
    _show_filter_summary(ano_selecionado, semana_selecionada, responsavel_selecionado, status_selecionados, df)
    
    return ano_selecionado, semana_selecionada, responsavel_selecionado, status_selecionados

def _create_responsavel_filter(df):
    """Cria filtro de responsável"""
    st.sidebar.subheader("👤 Responsável")
    responsaveis = ['Todos'] + sorted(df['RESPONSAVEL'].dropna().unique().tolist())
    return st.sidebar.selectbox("Responsável:", responsaveis)

def _create_status_filter(df):
    """Cria filtro de status com ícones"""
    st.sidebar.subheader("📊 Status dos Chamados")
    
    # Obter todos os status únicos
    status_unicos = sorted(df['STATUS'].dropna().unique().tolist())
    
    # Criar um mapeamento de status com ícones para melhor visualização
    status_mapping = {
        'Resolvido': '✅ Resolvido',
        'Fechado': '🔒 Fechado',
        'Cancelado': '❌ Cancelado',
        'Em Andamento': '🔄 Em Andamento',
        'Designado': '👤 Designado',
        'Pausa Equipe SCADA': '⏸️ Pausa Equipe SCADA',
        'Pendente Agendamento': '📅 Pendente Agendamento',
        'Pendente Aprovação': '📋 Pendente Aprovação',
        'Pendente Fornecedor': '🏢 Pendente Fornecedor',
        'Pendente Tarefa de TI': '💻 Pendente Tarefa de TI',
        'Pendente Usuário': '👥 Pendente Usuário'
    }
    
    # Criar lista de opções com ícones
    status_options = ['Todos os Status']
    status_display_map = {'Todos os Status': 'Todos'}
    
    for status in status_unicos:
        display_name = status_mapping.get(status, f"❓ {status}")
        status_options.append(display_name)
        status_display_map[display_name] = status
    
    # Multiselect para status
    status_selecionados_display = st.sidebar.multiselect(
        "Selecione os status:",
        options=status_options,
        default=['Todos os Status'],
        help="Selecione um ou mais status para filtrar os chamados"
    )
    
    # Converter de volta para os nomes originais dos status
    if 'Todos os Status' in status_selecionados_display or len(status_selecionados_display) == 0:
        return 'Todos'
    else:
        return [status_display_map[display] for display in status_selecionados_display]


def _create_requisicao_filter(df):
    """Cria filtro de busca por número de requisição com informações detalhadas"""
    st.sidebar.subheader("🔍 Buscar Requisição")
    
    # Input de busca
    numero_requisicao = st.sidebar.text_input(
        "Digite o número da requisição:",
        placeholder="Ex: 123456",
        help="Digite o número do chamado para ver todos os detalhes"
    )
    
    if numero_requisicao.strip():
        # Filtrar pela requisição
        df_requisicao = df[df['REQUISICAO'].astype(str).str.contains(numero_requisicao.strip(), case=False, na=False)]
        
        if len(df_requisicao) > 0:
            st.sidebar.success(f"✅ {len(df_requisicao)} requisição encontrada")
            
            # Mostrar detalhes de cada requisição encontrada
            for idx, row in df_requisicao.iterrows():
                with st.sidebar.expander(f"#{row['REQUISICAO']} - {row['STATUS']}", expanded=True):
                    st.write(f"**Status:** {row['STATUS']}")
                    st.write(f"**Responsável:** {row.get('RESPONSAVEL', 'N/A')}")
                    st.write(f"**Solicitante:** {row.get('SOLICITANTE', 'N/A')}")
                    st.write(f"**Resumo:** {row.get('RESUMO', row.get('TITULO', 'N/A'))}")
                    st.write(f"**Empresa:** {row.get('EMPRESA_SOLICITANTE', 'N/A')}")
                    st.write(f"**Cliente:** {row.get('CLIENTE_CIDADE', 'N/A')}")
                    st.write(f"**UF:** {row.get('CLIENTE_UF', 'N/A')}")
                    
                    st.write("---")
                    st.write("**📅 Datas:**")
                    
                    if pd.notna(row.get('DATA_ABERTURA')):
                        st.write(f"  • **Abertura:** {row['DATA_ABERTURA'].strftime('%d/%m/%Y')}")
                    else:
                        st.write(f"  • **Abertura:** N/A")
                    
                    if pd.notna(row.get('DATA_PREV_SOLUCAO')):
                        st.write(f"  • **Prev. Solução:** {row['DATA_PREV_SOLUCAO'].strftime('%d/%m/%Y')}")
                    else:
                        st.write(f"  • **Prev. Solução:** N/A")
                    
                    if pd.notna(row.get('DATA_ALVO')):
                        st.write(f"  • **Data Alvo:** {row['DATA_ALVO'].strftime('%d/%m/%Y')}")
                    else:
                        st.write(f"  • **Data Alvo:** N/A")
                    
                    if pd.notna(row.get('Data Esperada')):
                        st.write(f"  • **Data Esperada:** {row['Data Esperada'].strftime('%d/%m/%Y')}")
                    else:
                        st.write(f"  • **Data Esperada:** N/A")
                    
                    if pd.notna(row.get('DATA_RESOLUCAO')):
                        st.write(f"  • **Resolução:** {row['DATA_RESOLUCAO'].strftime('%d/%m/%Y')}")
                    else:
                        st.write(f"  • **Resolução:** N/A")
                    
                    if pd.notna(row.get('DATA_FECHAMENTO')):
                        st.write(f"  • **Fechamento:** {row['DATA_FECHAMENTO'].strftime('%d/%m/%Y')}")
                    else:
                        st.write(f"  • **Fechamento:** N/A")
                    
                    st.write("---")
                    sla_status = "🚨 Violado" if row.get('SLA_VIOLADO') else "✅ Ok"
                    st.write(f"**SLA:** {sla_status}")
        else:
            st.sidebar.warning(f"⚠️ Nenhuma requisição encontrada com '{numero_requisicao}'")


def _show_filter_summary(ano, semana, responsavel, status_selecionados, df):
    """Mostra resumo dos filtros aplicados"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Filtros Aplicados")
    st.sidebar.caption(f"**Ano:** {ano}")
    st.sidebar.caption(f"**Semana:** {semana}")
    st.sidebar.caption(f"**Responsável:** {responsavel}")
    
    if status_selecionados == 'Todos':
        status_unicos = sorted(df['STATUS'].dropna().unique().tolist())
        st.sidebar.caption(f"**Status:** Todos ({len(status_unicos)} tipos)")
    else:
        st.sidebar.caption(f"**Status:** {len(status_selecionados)} selecionado(s)")
        for status in status_selecionados[:3]:  # Mostrar até 3
            st.sidebar.caption(f"  • {status}")
        if len(status_selecionados) > 3:
            st.sidebar.caption(f"  • ... e mais {len(status_selecionados) - 3}")