import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.data_processor import get_display_status

def create_kanban_view(df, ano, semana, responsavel, status_filtrados):
    """Visualização Kanban - apenas chamados com status 'Resolvido' ficam na data de resolução"""
    
    # Inicializar estado para controlar exibição expandida
    if 'expanded_days' not in st.session_state:
        st.session_state.expanded_days = {}
    
    # Verificar se é semana atual
    semana_atual = datetime.now().isocalendar().week
    ano_atual = datetime.now().year
    is_current_week = (ano == ano_atual and semana == semana_atual)
    
    # Cabeçalho
    _create_header(responsavel, is_current_week, semana, ano)
    
    # Filtrar dados da semana
    df_filtered = _filter_data(df, ano, semana, responsavel, status_filtrados)
    
    if len(df_filtered) == 0:
        st.warning("⚠️ Nenhum chamado encontrado para esta semana com os filtros aplicados.")
        return
    
    # Mostrar informações sobre filtros aplicados
    _show_filter_info(status_filtrados)
    
    # Mostrar métricas da semana
    _show_week_metrics(df_filtered, ano, semana)
    
    # Criar visualização Kanban
    _create_week_kanban(df_filtered, ano, semana, responsavel, status_filtrados, is_current_week)

def _create_header(responsavel, is_current_week, semana, ano):
    """Cria cabeçalho da visualização"""
    if is_current_week:
        st.subheader(f"🔥 {responsavel if responsavel != 'Todos' else 'Visão Geral da Equipe'} - SEMANA ATUAL")
    else:
        st.subheader(f"{responsavel if responsavel != 'Todos' else 'Visão Geral da Equipe'}")
    
    # Ajustar descrição baseada na visualização
    if responsavel == 'Todos':
        st.caption(f"Semana {semana}/{ano} - Chamados por Data Alvo (Exibindo Responsável)")
    else:
        st.caption(f"Semana {semana}/{ano} - Chamados por Data Alvo (Resolvidos mostrados na data de resolução)")

def _filter_data(df, ano, semana, responsavel, status_filtrados):
    """Filtra dados da semana selecionada"""
    df_filtered = df[
        (df['ANO_ALVO'] == ano) & 
        (df['SEMANA_ALVO'] == semana)
    ].copy()
    
    if responsavel != 'Todos':
        df_filtered = df_filtered[df_filtered['RESPONSAVEL'] == responsavel]
    
    # Aplicar filtro de status
    if status_filtrados != 'Todos':
        df_filtered = df_filtered[df_filtered['STATUS'].isin(status_filtrados)]
    
    # Aplicar lógica de data de exibição
    df_filtered['DATA_DISPLAY'] = df_filtered.apply(_get_display_date, axis=1)
    
    return df_filtered

def _get_display_date(row):
    """Determina em que data o chamado deve aparecer no Kanban"""
    status_clean = str(row.get('STATUS', '')).strip()
    
    # MUDANÇA: agora inclui 'fechado' além de 'resolvido'
    if status_clean.lower() in ['resolvido', 'fechado'] and pd.notna(row.get('DATA_RESOLUCAO')):
        return row['DATA_RESOLUCAO'].date()
    else:
        return row['DATA_ALVO_DATE']

def _show_filter_info(status_filtrados):
    """Mostra informações sobre filtros aplicados"""
    if status_filtrados != 'Todos':
        st.info(f"📊 Filtrado por {len(status_filtrados)} status: {', '.join(status_filtrados[:3])}" + 
               (f" e mais {len(status_filtrados) - 3}" if len(status_filtrados) > 3 else ""))

def _show_week_metrics(df_filtered, ano, semana):
    """Mostra métricas da semana"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Aplicar lógica de exibição para métricas
    def get_display_date_for_metrics(row):
        """Determina em que data o chamado deve aparecer no Kanban - mesma lógica"""
        status_clean = str(row.get('STATUS', '')).strip()
        
        if status_clean.lower() in ['resolvido', 'fechado'] and pd.notna(row.get('DATA_RESOLUCAO')):
            return row['DATA_RESOLUCAO'].date()
        else:
            return row['DATA_ALVO_DATE']

    # Aplicar get_display_date nos dados filtrados
    df_filtered_copy = df_filtered.copy()
    df_filtered_copy['DATA_DISPLAY'] = df_filtered_copy.apply(get_display_date_for_metrics, axis=1)

    # Obter datas da semana para filtrar apenas chamados que aparecem no Kanban
    week_dates = get_week_dates(ano, semana)

    # Filtrar apenas chamados que aparecem na semana do Kanban
    df_kanban_visible = df_filtered_copy[df_filtered_copy['DATA_DISPLAY'].isin(week_dates)]

    # Calcular métricas baseadas apenas nos chamados visíveis no Kanban
    total_semana = len(df_kanban_visible)
    resolvidos = len(df_kanban_visible[df_kanban_visible['STATUS_CATEGORIA'].isin(['RESOLVIDO', 'FECHADO'])])
    em_aberto = len(df_kanban_visible[~df_kanban_visible['STATUS_CATEGORIA'].isin(['RESOLVIDO', 'FECHADO', 'CANCELADO'])])

    # Para SLA: considerar apenas chamados Resolvidos ou Fechados VISÍVEIS no Kanban
    df_sla_elegivel = df_kanban_visible[df_kanban_visible['STATUS'].isin(['Resolvido', 'Fechado'])]
    sla_violados = len(df_sla_elegivel[df_sla_elegivel['SLA_VIOLADO'] == True])
    total_sla_elegivel = len(df_sla_elegivel)

    with col1:
        st.metric("📋 Total", total_semana)
    with col2:
        st.metric("✅ Resolvidos", resolvidos, 
                 delta=f"{(resolvidos/total_semana*100):.1f}%" if total_semana > 0 else "0%")
    with col3:
        st.metric("⏳ Em Aberto", em_aberto,
                 delta=f"{(em_aberto/total_semana*100):.1f}%" if total_semana > 0 else "0%")
    with col4:
        st.metric("🚨 SLA Violado", sla_violados,
                 delta=f"{(sla_violados/total_sla_elegivel*100):.1f}%" if total_sla_elegivel > 0 else "0%")
    with col5:
        taxa_sla = ((total_sla_elegivel - sla_violados) / total_sla_elegivel * 100) if total_sla_elegivel > 0 else 100
        st.metric("🎯 Taxa SLA", f"{taxa_sla:.1f}%",
                 delta="✅ Ok" if taxa_sla >= 95 else "⚠️ Atenção")

def _create_week_kanban(df_filtered, ano, semana, responsavel, status_filtrados, is_current_week):
    """Cria visualização Kanban por dia da semana"""
    week_dates = get_week_dates(ano, semana)
    days_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    cols = st.columns(7)
    
    for i, (col, day_pt, date) in enumerate(zip(cols, days_pt, week_dates)):
        with col:
            _create_day_column(df_filtered, day_pt, date, ano, semana, responsavel, 
                             status_filtrados, is_current_week)

def _create_day_column(df_filtered, day_pt, date, ano, semana, responsavel, status_filtrados, is_current_week):
    """Cria coluna de um dia específico no Kanban"""
    # USAR DATA_DISPLAY ao invés de DATA_ALVO_DATE
    day_tickets = df_filtered[df_filtered['DATA_DISPLAY'] == date]
    total_dia = len(day_tickets)
    
    # Verificar se é hoje
    hoje = datetime.now().date()
    is_today = date == hoje
    
    # Criar chave única para este dia
    status_key = "_".join(status_filtrados) if status_filtrados != 'Todos' else 'todos'
    day_key = f"{ano}_{semana}_{responsavel}_{date}_{status_key}"
    
    # Header do dia
    header_info = f"{total_dia} chamados"
    
    if is_today and is_current_week:
        st.markdown(f'''
            <div class="current-week-header">
                {day_pt} - HOJE<br>
                {date.strftime("%d/%m")}<br>
                <small>{header_info}</small>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="day-header">
                {day_pt}<br>
                {date.strftime("%d/%m")}<br>
                <small>{header_info}</small>
            </div>
        ''', unsafe_allow_html=True)
    
    if total_dia == 0:
        st.info("Sem chamados")
    else:
        _show_day_tickets(day_tickets, day_key, total_dia, responsavel)

def _show_day_tickets(day_tickets, day_key, total_dia, responsavel):
    """Mostra tickets do dia com opção de expandir/recolher"""
    # Verificar se este dia está expandido
    is_expanded = st.session_state.expanded_days.get(day_key, False)
    
    # Determinar quantos cards mostrar
    if is_expanded:
        tickets_to_show = day_tickets
    else:
        tickets_to_show = day_tickets.head(5)
    
    # Mostrar tickets
    for idx, ticket in tickets_to_show.iterrows():
        _create_ticket_card(ticket, responsavel)
    
    # Mostrar botões de expansão/recolhimento
    _show_expansion_buttons(total_dia, is_expanded, day_key)

def _create_ticket_card(ticket, responsavel):
    """Cria card individual do ticket com animação de vibração"""
    # Determinar classe CSS baseada no status
    status_cat = ticket['STATUS_CATEGORIA'].lower()
    card_class = f"kanban-card-{status_cat.replace('_', '-')}"
    
    # NOVA LÓGICA: Adicionar classe de vibração se necessário
    vibrate_class = ""
    urgent_class = ""
    if ticket.get('SHOULD_VIBRATE', False):
        vibrate_class = "vibrating-card"
        urgent_class = "urgent-card"
    
    # Combinar todas as classes
    all_classes = f"kanban-card {card_class} {vibrate_class} {urgent_class}".strip()
    
    # Preparar contador de dias se aplicável
    contador_dias = ""
    if ticket['CONTADOR_DIAS']:
        contador_dias = f'({ticket["CONTADOR_DIAS"]})'
    
    # NOVA LÓGICA: Decidir o que mostrar baseado na visualização
    if responsavel == 'Todos':
        # Na visualização "Todos", mostrar o responsável (primeiro e segundo nome)
        display_info = _get_short_name(ticket.get('RESPONSAVEL', 'N/A'))
        info_label = "Responsável"
    else:
        # Na visualização individual, mostrar o status
        display_info = get_display_status(ticket.get('STATUS', 'N/A'))
        info_label = "Status"
    
    st.markdown(f'''
        <div class="{all_classes}">
            <strong>#{ticket.get('REQUISICAO', 'N/A')} {ticket['STATUS_ICONE']}</strong><br>
            <small><strong>{info_label}:</strong> {display_info} {contador_dias}</small>
        </div>
    ''', unsafe_allow_html=True)

def _get_short_name(full_name):
    """Extrai o primeiro e segundo nome de um nome completo"""
    if not full_name or full_name == 'N/A' or str(full_name).strip() == '':
        return 'Sem Responsável'
    
    # Limpar e dividir o nome
    name_parts = str(full_name).strip().split()
    
    if len(name_parts) == 0:
        return 'Sem Responsável'
    elif len(name_parts) == 1:
        return name_parts[0]
    elif len(name_parts) >= 2:
        return f"{name_parts[0]} {name_parts[1]}"
    else:
        return str(full_name)[:20]  # Fallback: primeiros 20 caracteres

def _show_expansion_buttons(total_dia, is_expanded, day_key):
    """Mostra botões de expansão/recolhimento se necessário"""
    # Mostrar botão "Veja +" se houver mais de 5 chamados e não estiver expandido
    if total_dia > 5 and not is_expanded:
        if st.button(f"Veja + ({total_dia - 5} mais)", key=f"btn_expand_{day_key}", 
                    use_container_width=True):
            st.session_state.expanded_days[day_key] = True
            st.rerun()
    
    # Mostrar botão "Mostrar menos" se estiver expandido e houver mais de 5
    elif total_dia > 5 and is_expanded:
        if st.button("Mostrar menos", key=f"btn_collapse_{day_key}", 
                    use_container_width=True):
            st.session_state.expanded_days[day_key] = False
            st.rerun()

def get_week_dates(year, week):
    """Obtém as datas da semana específica"""
    try:
        # Criar data do primeiro dia do ano
        jan_1 = datetime(year, 1, 1)
        
        # Encontrar a primeira segunda-feira da semana 1 ISO
        days_since_monday = jan_1.weekday()
        days_to_first_monday = -days_since_monday if days_since_monday != 0 else 0
        
        first_monday = jan_1 + timedelta(days=days_to_first_monday)
        week_start = first_monday + timedelta(weeks=week-1)
        
        week_dates = []
        for i in range(7):
            current_date = week_start + timedelta(days=i)
            week_dates.append(current_date.date())
        
        return week_dates
    except:
        # Fallback para a semana atual
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        return [week_start + timedelta(days=i) for i in range(7)]