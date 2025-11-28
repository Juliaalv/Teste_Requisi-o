import pandas as pd

def get_display_date(row):
    """
    Determina a data de exibição do chamado no Kanban/Analytics
    
    Regra:
    - Se RESOLVIDO/FECHADO e tem DATA_RESOLUCAO: usa DATA_RESOLUCAO
    - Caso contrário: usa DATA_ALVO_DATE
    """
    status_clean = str(row.get('STATUS', '')).strip().lower()
    
    if status_clean in ['resolvido', 'fechado'] and pd.notna(row.get('DATA_RESOLUCAO')):
        return row['DATA_RESOLUCAO'].date()
    else:
        return row['DATA_ALVO_DATE']