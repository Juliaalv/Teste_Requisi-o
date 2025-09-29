import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from components.kanban import get_week_dates

def create_analytics(df, ano, semana, responsavel, status_filtrados):
    """Cria análises focadas na DATA_ALVO com gráfico de barras empilhadas"""
    st.subheader("📊 Análise de Dados")
    
    # Filtrar dados
    df_filtered = _filter_analytics_data(df, ano, semana, responsavel, status_filtrados)
    
    if len(df_filtered) == 0:
        st.info("Nenhum dado para análise com os filtros selecionados.")
        return
    
    # Criar abas para diferentes análises
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Por Data Alvo", "🎯 Análise SLA", "👥 Por Responsável", "📊 Programados vs Extras", "📋 Lista Detalhada"])
    
    with tab1:
        _create_data_alvo_analysis(df_filtered, ano, semana)
    
    with tab2:
        _create_sla_analysis(df_filtered, responsavel, status_filtrados, df)
    
    with tab3:
        _create_responsavel_analysis(df_filtered, responsavel)
    
    with tab4:
        _create_programados_extras_analysis(df_filtered, ano, semana)
    
    with tab5:
        _create_detailed_list(df_filtered)

def _filter_analytics_data(df, ano, semana, responsavel, status_filtrados):
    """Filtra dados para análise - MESMA LÓGICA DO KANBAN"""
    
    # PRIMEIRO: Filtrar por DATA_ALVO
    df_data_alvo = df[
        (df['ANO_ALVO'] == ano) & 
        (df['SEMANA_ALVO'] == semana)
    ].copy()
    
    # SEGUNDO: Adicionar chamados RESOLVIDOS/FECHADOS nesta semana
    df_temp = df.copy()
    df_temp['DATA_RESOLUCAO_VALIDA'] = pd.notna(df_temp['DATA_RESOLUCAO'])
    df_temp['SEMANA_RESOLUCAO'] = df_temp['DATA_RESOLUCAO'].dt.isocalendar().week
    df_temp['ANO_RESOLUCAO'] = df_temp['DATA_RESOLUCAO'].dt.year
    
    df_resolvidos_semana = df_temp[
        (df_temp['STATUS'].isin(['Resolvido', 'Fechado'])) &
        (df_temp['DATA_RESOLUCAO_VALIDA']) &
        (df_temp['ANO_RESOLUCAO'] == ano) &
        (df_temp['SEMANA_RESOLUCAO'] == semana)
    ].copy()
    
    # TERCEIRO: Combinar removendo duplicatas
    df_filtered = pd.concat([df_data_alvo, df_resolvidos_semana]).drop_duplicates(subset=['REQUISICAO'])
    
    # Aplicar filtros adicionais
    if responsavel != 'Todos':
        df_filtered = df_filtered[df_filtered['RESPONSAVEL'] == responsavel]
    
    if status_filtrados != 'Todos':
        df_filtered = df_filtered[df_filtered['STATUS'].isin(status_filtrados)]
    
    return df_filtered

def _create_data_alvo_analysis(df_filtered, ano, semana):
    """Cria análise por data alvo"""
    col1, col2 = st.columns(2)
    
    with col1:
        _create_stacked_bar_chart(df_filtered, ano, semana)
    
    with col2:
        _create_status_pie_chart(df_filtered, ano, semana)
    
    # Tabela resumo
    _create_summary_table(df_filtered, ano, semana)

def _create_stacked_bar_chart(df_filtered, ano, semana):
    """Cria gráfico de barras empilhadas"""
    def get_display_date_analytics(row):
        """Mesma lógica do get_display_date do Kanban"""
        status_clean = str(row.get('STATUS', '')).strip()
        
        if status_clean.lower() in ['resolvido', 'fechado'] and pd.notna(row.get('DATA_RESOLUCAO')):
            return row['DATA_RESOLUCAO'].date()
        else:
            return row['DATA_ALVO_DATE']
    
    # Aplicar get_display_date nos dados filtrados
    df_analytics = df_filtered.copy()
    df_analytics['DATA_DISPLAY'] = df_analytics.apply(get_display_date_analytics, axis=1)
    
    # Obter datas da semana para filtrar apenas chamados que aparecem no Kanban
    week_dates = get_week_dates(ano, semana)
    
    # Filtrar apenas chamados que aparecem na semana do Kanban
    df_kanban_visible = df_analytics[df_analytics['DATA_DISPLAY'].isin(week_dates)]
    
    # Gráfico de barras empilhadas por DATA_DISPLAY
    if len(df_kanban_visible) > 0:
        grouped_data = df_kanban_visible.groupby(['DATA_DISPLAY', 'STATUS']).size().reset_index(name='Quantidade')
        
        fig = px.bar(
            grouped_data, 
            x='DATA_DISPLAY', 
            y='Quantidade',
            color='STATUS',
            title=f"Chamados Visíveis no Kanban - Semana {semana}/{ano}",
            color_discrete_map=_get_status_colors(),
            labels={'DATA_DISPLAY': 'Data de Exibição no Kanban', 'Quantidade': 'Quantidade de Chamados'}
        )
        
        fig.update_layout(
            xaxis_title="Data de Exibição no Kanban",
            yaxis_title="Quantidade de Chamados",
            legend_title="Status",
            hovermode='x unified'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{fullData.name}</b><br>Data: %{x}<br>Quantidade: %{y}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True, key="chart_stacked_bar")
    else:
        st.info("Não há dados suficientes para o gráfico empilhado.")

def _create_status_pie_chart(df_filtered, ano, semana):
    """Cria gráfico pizza de distribuição por status"""
    # Aplicar mesma lógica para consistência
    df_analytics = df_filtered.copy()
    df_analytics['DATA_DISPLAY'] = df_analytics.apply(lambda row: row['DATA_RESOLUCAO'].date() 
                                                     if str(row.get('STATUS', '')).strip().lower() in ['resolvido', 'fechado'] 
                                                        and pd.notna(row.get('DATA_RESOLUCAO'))
                                                     else row['DATA_ALVO_DATE'], axis=1)
    
    week_dates = get_week_dates(ano, semana)
    df_kanban_visible = df_analytics[df_analytics['DATA_DISPLAY'].isin(week_dates)]
    
    if len(df_kanban_visible) > 0:
        status_counts = df_kanban_visible['STATUS'].value_counts().head(10)
        
        fig_pie = px.pie(
            values=status_counts.values, 
            names=status_counts.index,
            title=f"Status dos Chamados Visíveis - Semana {semana}/{ano}",
            color_discrete_map=_get_status_colors()
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="chart_status_dist_1")
    else:
        st.info("Não há dados para o gráfico de distribuição.")

def _create_summary_table(df_filtered, ano, semana):
    """Cria tabela resumo por data e status"""
    st.subheader(f"Resumo dos Chamados Visíveis no Kanban - Semana {semana}/{ano}")
    
    # Aplicar mesma lógica para consistência
    df_analytics = df_filtered.copy()
    df_analytics['DATA_DISPLAY'] = df_analytics.apply(lambda row: row['DATA_RESOLUCAO'].date() 
                                                     if str(row.get('STATUS', '')).strip().lower() in ['resolvido', 'fechado'] 
                                                        and pd.notna(row.get('DATA_RESOLUCAO'))
                                                     else row['DATA_ALVO_DATE'], axis=1)
    
    week_dates = get_week_dates(ano, semana)
    df_kanban_visible = df_analytics[df_analytics['DATA_DISPLAY'].isin(week_dates)]
    
    if len(df_kanban_visible) > 0:
        pivot_table = df_kanban_visible.groupby(['DATA_DISPLAY', 'STATUS']).size().unstack(fill_value=0)
        pivot_table['Total'] = pivot_table.sum(axis=1)
        pivot_table = pivot_table.sort_values('Total', ascending=False).head(15)
        
        # Renomear índice para ficar mais claro
        pivot_table.index.name = 'Data de Exibição no Kanban'
        
        st.dataframe(pivot_table, use_container_width=True)
    else:
        st.info("Nenhum chamado visível no Kanban para esta semana.")

def _create_sla_analysis(df_filtered, responsavel, status_filtrados, df):
    """Cria análise de SLA"""
    col1, col2 = st.columns(2)
    
    with col1:
        _create_sla_pie_chart(df_filtered)
    
    with col2:
        _create_sla_weekly_chart(df_filtered, responsavel, status_filtrados, df)

def _create_sla_pie_chart(df_filtered):
    """Cria gráfico pizza do status SLA"""
    # Status do SLA - APENAS RESOLVIDOS/FECHADOS
    df_sla_elegivel = df_filtered[df_filtered['STATUS'].isin(['Resolvido', 'Fechado'])]
    
    if len(df_sla_elegivel) > 0:
        sla_data = df_sla_elegivel['SLA_VIOLADO'].value_counts()
        sla_labels = {True: 'SLA Violado', False: 'SLA OK'}
        
        fig = px.pie(
            values=sla_data.values, 
            names=[sla_labels[x] for x in sla_data.index],
            title=f"Status do SLA - Apenas Resolvidos/Fechados ({len(df_sla_elegivel)} chamados)",
            color_discrete_map={'SLA Violado': '#dc3545', 'SLA OK': '#28a745'}
        )
        st.plotly_chart(fig, use_container_width=True, key="chart_sla_status_1")
    else:
        st.info("Nenhum chamado resolvido/fechado encontrado para análise de SLA.")

def _create_sla_weekly_chart(df_filtered, responsavel, status_filtrados, df):
    """Cria gráfico de taxa SLA por semana"""
    # Chamados por semana - APENAS RESOLVIDOS/FECHADOS
    df_sla_weekly = df[df['STATUS'].isin(['Resolvido', 'Fechado'])]
    
    if responsavel != 'Todos':
        df_sla_weekly = df_sla_weekly[df_sla_weekly['RESPONSAVEL'] == responsavel]
    
    if status_filtrados != 'Todos':
        df_sla_weekly = df_sla_weekly[df_sla_weekly['STATUS'].isin(status_filtrados)]
    
    weekly_data = df_sla_weekly.groupby(['ANO_ALVO', 'SEMANA_ALVO']).agg({
        'REQUISICAO': 'count',
        'SLA_VIOLADO': 'sum'
    }).reset_index()
    
    weekly_data['Semana_Label'] = weekly_data['SEMANA_ALVO'].astype(str) + '/' + weekly_data['ANO_ALVO'].astype(str)
    weekly_data['Taxa_SLA'] = ((weekly_data['REQUISICAO'] - weekly_data['SLA_VIOLADO']) / weekly_data['REQUISICAO'] * 100).round(1)
    
    if len(weekly_data) > 0:
        fig = px.line(
            weekly_data.tail(10), 
            x='Semana_Label', 
            y='Taxa_SLA',
            title="Taxa de SLA por Semana (%) - Apenas Resolvidos/Fechados",
            color_discrete_sequence=['#28a745']
        )
        fig.add_hline(y=95, line_dash="dash", line_color="red", 
                     annotation_text="Meta: 95%")
        st.plotly_chart(fig, use_container_width=True, key="chart_sla_weekly_1")
    else:
        st.info("Dados insuficientes para análise temporal de SLA.")

def _create_responsavel_analysis(df_filtered, responsavel):
    """Cria análise por responsável"""
    if responsavel == 'Todos':
        col1, col2 = st.columns(2)
        
        with col1:
            _create_backlog_chart(df_filtered)
        
        with col2:
            _create_total_responsavel_chart(df_filtered)
        
        # Criar tabela consolidada
        _create_responsavel_table(df_filtered)
    else:
        st.info("Análise de backlog disponível apenas na visão 'Todos'.")

def _create_programados_extras_analysis(df_filtered, ano, semana):
    """Análise de programados vs extras com lógica refinada"""
    st.caption("Compara chamados programados vs extras (baseado na lógica de resolução).")

    week_dates = get_week_dates(ano, semana)
    days_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    # Preparar dados para o gráfico
    programados_extras_data = []

    col1, col2 = st.columns(2)
    with col1:
        for i, date in enumerate(week_dates):
            day_name = days_pt[i]
            day_label = f"{day_name}\n{date.strftime('%d/%m')}"
            
            # PROGRAMADOS: Chamados resolvidos/fechados onde DATA_RESOLUCAO = DATA_ALVO
            programados_df = df_filtered[
                (df_filtered['STATUS'].isin(['Resolvido', 'Fechado'])) &
                (df_filtered['DATA_RESOLUCAO'].notna()) &
                (df_filtered['DATA_RESOLUCAO'].dt.date == date) &
                (df_filtered['DATA_ALVO_DATE'] == date)
            ]
            qtd_programados = len(programados_df)

            # EXTRAS: Chamados resolvidos neste dia mas programados para outro dia
            extras_df = df_filtered[
                (df_filtered['STATUS'].isin(['Resolvido', 'Fechado'])) &
                (df_filtered['DATA_RESOLUCAO'].notna()) &
                (df_filtered['DATA_RESOLUCAO'].dt.date == date) &
                (df_filtered['DATA_ALVO_DATE'] != date)
            ]
            qtd_extras = len(extras_df)
            
            # Adicionar dados para o gráfico
            if qtd_programados > 0:
                programados_extras_data.append({
                    'Dia': day_label,
                    'Tipo': 'Programados',
                    'Quantidade': qtd_programados,
                    'Data': date
                })
            
            if qtd_extras > 0:
                programados_extras_data.append({
                    'Dia': day_label,
                    'Tipo': 'Extras',
                    'Quantidade': qtd_extras,
                    'Data': date
                })
        
        if programados_extras_data:
            df_prog_extra = pd.DataFrame(programados_extras_data)
            
            # Criar gráfico de barras empilhadas
            fig = px.bar(
                df_prog_extra,
                x='Dia',
                y='Quantidade',
                color='Tipo',
                title=f"Programados vs Extras por Dia - Semana {semana}/{ano}",
                color_discrete_map={
                    'Programados': '#007bff',
                    'Extras': '#28a745'
                },
                barmode='stack'
            )
            
            fig.update_layout(
                xaxis_title="Dia da Semana",
                yaxis_title="Quantidade de Chamados",
                legend_title="Tipo de Chamado",
                hovermode='x unified'
            )
            
            fig.update_traces(
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Quantidade: %{y}<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="chart_programados_extras")
            
    with col2:
        st.subheader("Resumo por Dia")
        
        # Criar tabela resumo
        resumo_data = []
        for i, date in enumerate(week_dates):
            day_name = days_pt[i]
            
            # Programados
            programados_count = len(df_filtered[
                (df_filtered['STATUS'].isin(['Resolvido', 'Fechado'])) &
                (df_filtered['DATA_RESOLUCAO'].notna()) &
                (df_filtered['DATA_RESOLUCAO'].dt.date == date) &
                (df_filtered['DATA_ALVO_DATE'] == date)
            ])

            # Extras
            extras_count = len(df_filtered[
                (df_filtered['STATUS'].isin(['Resolvido', 'Fechado'])) &
                (df_filtered['DATA_RESOLUCAO'].notna()) &
                (df_filtered['DATA_RESOLUCAO'].dt.date == date) &
                (df_filtered['DATA_ALVO_DATE'] != date)
            ])

            if programados_count > 0 or extras_count > 0:
                resumo_data.append({
                    'Dia': f"{day_name} ({date.strftime('%d/%m')})",
                    'Programados': programados_count,
                    'Extras': extras_count,
                    'Total': programados_count + extras_count
                })
            
        if resumo_data:
            df_resumo = pd.DataFrame(resumo_data)
            st.dataframe(df_resumo, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum dado para resumo")

def _create_backlog_chart(df_filtered):
    """Cria gráfico de backlog por responsável"""
    status_finalizados = ['Resolvido', 'Fechado', 'Cancelado']
    backlog_data = df_filtered[~df_filtered['STATUS'].isin(status_finalizados)].copy()
    
    if len(backlog_data) > 0:
        backlog_grouped = backlog_data.groupby(['RESPONSAVEL', 'STATUS']).size().reset_index(name='Quantidade')
        
        cores_status = _get_backlog_colors()
        
        # Calcular total por responsável para ordenação
        total_por_responsavel = backlog_grouped.groupby('RESPONSAVEL')['Quantidade'].sum().sort_values(ascending=True)
        
        fig = go.Figure()
        
        # Adicionar uma barra para cada status
        for status in backlog_grouped['STATUS'].unique():
            status_data = backlog_grouped[backlog_grouped['STATUS'] == status]
            status_data = status_data.set_index('RESPONSAVEL').reindex(total_por_responsavel.index, fill_value=0).reset_index()
            
            fig.add_trace(go.Bar(
                name=status,
                y=status_data['RESPONSAVEL'],
                x=status_data['Quantidade'],
                orientation='h',
                marker_color=cores_status.get(status, '#6c757d'),
                hovertemplate=f'<b>%{{y}}</b><br>{status}: %{{x}}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Backlog por Responsável - Status em Aberto',
            xaxis_title='Quantidade de Chamados',
            yaxis_title='Responsável',
            barmode='stack',
            height=max(400, len(total_por_responsavel) * 30),
            showlegend=True,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01)
        )
        
        st.plotly_chart(fig, use_container_width=True, key="chart_backlog_responsavel")
    else:
        st.info("Não há chamados em aberto no período.")

def _create_total_responsavel_chart(df_filtered):
    """Cria gráfico total por responsável"""
    total_por_resp = df_filtered.groupby('RESPONSAVEL').size().sort_values(ascending=True)
    
    fig_total = go.Figure(go.Bar(
        y=total_por_resp.index,
        x=total_por_resp.values,
        orientation='h',
        marker_color='#17a2b8',
        hovertemplate='<b>%{y}</b><br>Total: %{x}<extra></extra>'
    ))
    
    fig_total.update_layout(
        title='Volume Total de Chamados por Responsável',
        xaxis_title='Total de Chamados',
        yaxis_title='Responsável',
        height=max(400, len(total_por_resp) * 30)
    )
    
    st.plotly_chart(fig_total, use_container_width=True, key="chart_total_responsavel")

def _create_responsavel_table(df_filtered):
    """Cria tabela consolidada por responsável"""
    tabela_consolidada = []
    for responsavel in df_filtered['RESPONSAVEL'].unique():
        dados_resp = df_filtered[df_filtered['RESPONSAVEL'] == responsavel]
        
        total_chamados = len(dados_resp)
        resolvidos = len(dados_resp[dados_resp['STATUS'] == 'Resolvido'])
        fechados = len(dados_resp[dados_resp['STATUS'] == 'Fechado'])
        em_andamento = len(dados_resp[dados_resp['STATUS'] == 'Em Andamento'])
        designados = len(dados_resp[dados_resp['STATUS'] == 'Designado'])
        pausados = len(dados_resp[dados_resp['STATUS'] == 'Pausa Equipe SCADA'])
        pendentes = len(dados_resp[dados_resp['STATUS'].str.contains('Pendente', na=False)])
        
        finalizados = resolvidos + fechados
        backlog_ativo = total_chamados - finalizados
        
        tabela_consolidada.append({
            'Responsável': responsavel,
            'Total': total_chamados,
            'Finalizados': finalizados,
            'Backlog Ativo': backlog_ativo,
            'Em Andamento': em_andamento,
            'Designado': designados,
            'Em Pausa': pausados,
            'Pendentes': pendentes,
            '% Finalizado': round((finalizados / total_chamados * 100) if total_chamados > 0 else 0, 1)
        })
    
    # Converter para DataFrame e ordenar por backlog ativo
    df_consolidado = pd.DataFrame(tabela_consolidada)
    df_consolidado = df_consolidado.sort_values('Backlog Ativo', ascending=False)
    
    st.dataframe(df_consolidado, use_container_width=True, hide_index=True)

def _create_detailed_list(df_filtered):
    """Cria lista detalhada de chamados"""
    display_cols = ['REQUISICAO', 'DATA_ALVO', 'STATUS', 'RESUMO', 'RESPONSAVEL', 'SLA_VIOLADO']
    available_cols = [col for col in display_cols if col in df_filtered.columns]
    
    # Ordenar por data alvo
    df_display = df_filtered.sort_values('DATA_ALVO', ascending=False)
    
    st.dataframe(df_display[available_cols].head(100), use_container_width=True, hide_index=True)
    
    if len(df_display) > 100:
        st.caption(f"Mostrando 100 de {len(df_display)} chamados")

def _get_status_colors():
    """Retorna mapeamento de cores para status"""
    return {
        'Resolvido': '#28a745',
        'Fechado': '#17a2b8', 
        'Designado': '#6f42c1',
        'Em Andamento': '#007bff',
        'Cancelado': '#dc3545',
        'Pendente Agendamento': '#ffc107',
        'Pendente Aprovação': '#ffc107',
        'Pendente Fornecedor': '#ffc107',
        'Pendente Tarefa de TI': '#ffc107',
        'Pendente Usuário': '#ffc107',
        'Pausa Equipe SCADA': '#fd7e14'
    }

def _get_backlog_colors():
    """Retorna mapeamento de cores para status de backlog"""
    return {
        'Em Andamento': '#007bff',
        'Designado': '#6f42c1',
        'Pausa Equipe SCADA': '#fd7e14',
        'Pendente Agendamento': '#ffc107',
        'Pendente Aprovação': '#ffc107',
        'Pendente Fornecedor': '#ffc107',
        'Pendente Tarefa de TI': '#ffc107',
        'Pendente Usuário': '#ffc107'
    }