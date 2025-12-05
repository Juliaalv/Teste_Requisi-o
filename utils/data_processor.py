import pandas as pd
import streamlit as st
from datetime import datetime

def get_display_status(status):
    """Padroniza nomes de status apenas para exibição nos cards"""
    status_display_map = {
        'Pendente Agendamento': 'Agendamento',
        'Pendente Equipe SCADA': 'Pendente SCADA',
        'Pausa Equipe SCADA': 'Pausa SCADA',
        'Pendente Tarefa de TI': 'Pendente TI',
        'Pendente Fornecedor': 'Fornecedor'
    }
    return status_display_map.get(status, status)

def prepare_data_with_real_status(df):
    """Preparação dos dados com os status reais do sistema - usando DATA_ALVO"""
    
    # Verificar se temos uma coluna de data alvo disponível
    data_alvo_col = None
    possible_date_cols = ['DATA_ALVO', 'DATA_PREV_SOLUCAO', 'DATA_LIMITE_SLA']
    
    for col in possible_date_cols:
        if col in df.columns:
            data_alvo_col = col
            break
    
    if data_alvo_col is None:
        st.error("⚠ Nenhuma coluna de data alvo encontrada!")
        st.info("Colunas disponíveis: " + ", ".join(df.columns.tolist()))
        return df
    
    # Se não for DATA_ALVO, renomear
    if data_alvo_col != 'DATA_ALVO':
        df = df.rename(columns={data_alvo_col: 'DATA_ALVO'})
        st.info(f"📅 Usando coluna '{data_alvo_col}' como DATA_ALVO")
    
    # Converter datas
    date_columns = ['DATA_ABERTURA', 'DATA_ALVO', 'DATA_RESOLUCAO', 'DATA_PREV_SOLUCAO']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Filtrar apenas registros com DATA_ALVO válida
    df = df[df['DATA_ALVO'].notna()].copy()
    
    # NOVA LÓGICA: Se Data Esperada existe e passou da Data Esperada, usar DATA_PREV_SOLUCAO como DATA_ALVO
    hoje = datetime.now().date()
    if 'Data Esperada' in df.columns:
        df['Data Esperada'] = pd.to_datetime(df['Data Esperada'], errors='coerce')
        
        # Se passou da Data Esperada, usar DATA_PREV_SOLUCAO
        def ajustar_data_alvo(row):
            if pd.notna(row.get('Data Esperada')):
                data_esperada = row['Data Esperada'].date()
                # Se hoje é depois da data esperada, retornar DATA_PREV_SOLUCAO
                if hoje > data_esperada and pd.notna(row.get('DATA_PREV_SOLUCAO')):
                    return row['DATA_PREV_SOLUCAO']
            return row['DATA_ALVO']
        
        df['DATA_ALVO'] = df.apply(ajustar_data_alvo, axis=1)
    
    # Criar colunas auxiliares baseadas na DATA_ALVO
    df['DATA_ALVO_DATE'] = df['DATA_ALVO'].dt.date
    df['SEMANA_ALVO'] = df['DATA_ALVO'].dt.isocalendar().week
    df['ANO_ALVO'] = df['DATA_ALVO'].dt.year
    
    def should_vibrate(row):
        """Verifica se o card deve vibrar - apenas quando DATA_ALVO = DATA_PREV_SOLUCAO = DIA ATUAL e status em aberto"""
        # Obter data atual
        hoje = datetime.now().date()
        
        # Verificar se as datas são válidas
        if pd.notna(row.get('DATA_PREV_SOLUCAO')) and pd.notna(row.get('DATA_ALVO')):
            data_alvo = row['DATA_ALVO'].date()
            data_prev = row['DATA_PREV_SOLUCAO'].date()
            
            # Verificar se DATA_ALVO = DATA_PREV_SOLUCAO = HOJE
            dates_match_and_today = (data_alvo == data_prev == hoje)
            
            # Verificar se o status NÃO é finalizado (Resolvido, Fechado, Cancelado)
            status_finalizados = ['Resolvido', 'Fechado', 'Cancelado']
            status_atual = str(row.get('STATUS', '')).strip()
            status_em_aberto = status_atual not in status_finalizados
            
            # Vibrar apenas se: DATA_ALVO = DATA_PREV_SOLUCAO = HOJE E status em aberto
            return dates_match_and_today and status_em_aberto
        return False
    
    df['SHOULD_VIBRATE'] = df.apply(should_vibrate, axis=1)
    
    def calcular_diferenca_dias(row):
        if pd.notna(row.get('DATA_RESOLUCAO')) and row.get('STATUS') in ['Resolvido', 'Fechado']:
            diferenca = (row['DATA_ALVO_DATE'] - row['DATA_RESOLUCAO'].date()).days
            if diferenca > 0:
                return f"+{diferenca}"  # Resolvido antes da data alvo (sobrou tempo)
            elif diferenca < 0:
                return f"{diferenca}"  # Resolvido depois da data alvo (atrasou)
            else:
                return "0"  # Resolvido na data exata
        return ""
    
    df['CONTADOR_DIAS'] = df.apply(calcular_diferenca_dias, axis=1)
    
    # Filtrar anos válidos 
    ano_atual = datetime.now().year
    df = df[(df['ANO_ALVO'] >= 2020) & (df['ANO_ALVO'] <= ano_atual + 2)].copy()
    
    # Mapear status reais para categorias com cores
    status_mapping = {
        'Resolvido': {'categoria': 'RESOLVIDO', 'cor': '#28a745', 'icone': '✅'},
        'Fechado': {'categoria': 'FECHADO', 'cor': '#17a2b8', 'icone': '🔒'},
        'Cancelado': {'categoria': 'CANCELADO', 'cor': '#dc3545', 'icone': '❌'},
        'Em Andamento': {'categoria': 'EM_ANDAMENTO', 'cor': '#007bff', 'icone': '🔄'},
        'Designado': {'categoria': 'DESIGNADO', 'cor': '#6f42c1', 'icone': '👤'},
        'Pausa Equipe SCADA': {'categoria': 'PAUSA', 'cor': '#fd7e14', 'icone': '⏸️'},
        'Pendente Agendamento': {'categoria': 'PENDENTE', 'cor': '#ffc107', 'icone': '📅'},
        'Pendente Aprovação': {'categoria': 'PENDENTE', 'cor': '#ffc107', 'icone': '📋'},
        'Pendente Fornecedor': {'categoria': 'PENDENTE', 'cor': '#ffc107', 'icone': '🏢'},
        'Pendente Tarefa de TI': {'categoria': 'PENDENTE', 'cor': '#ffc107', 'icone': '💻'},
        'Pendente Usuário': {'categoria': 'PENDENTE', 'cor': '#ffc107', 'icone': '👥'}
    }
    
    # Aplicar mapeamento
    def get_status_info(status):
        status_clean = str(status).strip() if pd.notna(status) else 'Desconhecido'
        info = status_mapping.get(status_clean, {
            'categoria': 'OUTROS', 
            'cor': '#6c757d', 
            'icone': '❓'
        })
        return info
    
    df['STATUS_CATEGORIA'] = df['STATUS'].apply(lambda x: get_status_info(x)['categoria'])
    df['STATUS_ICONE'] = df['STATUS'].apply(lambda x: get_status_info(x)['icone'])
    
    # Garantir que SLA_VIOLADO seja booleano
    if 'SLA_VIOLADO' in df.columns:
        df['SLA_VIOLADO'] = df['SLA_VIOLADO'].fillna(False)
        df['SLA_VIOLADO'] = df['SLA_VIOLADO'].astype(bool)
    else:
        df['SLA_VIOLADO'] = False
    
    return df