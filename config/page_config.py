import streamlit as st

def configure_page():
    """Configura a página do Streamlit"""
    st.set_page_config(
        page_title="Análise de Chamados",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS customizado - ATUALIZADO com animações
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #666;
        text-align: center;
        padding: 15px 0;
        font-size: 0.9rem;
        border-top: 1px solid #ddd;
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }
    .footer-logo {
        height: 30px;
        width: auto;
    }
    .footer-text {
        margin: 0;
    }
    .main-content {
        margin-bottom: 80px;
    }
    .kanban-card {
        background-color: #f8f9fa;
        padding: 12px;
        margin: 5px 0;
        border-radius: 8px;
        border-left: 4px solid;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }

    /* ANIMAÇÃO DE VIBRAÇÃO */
    .vibrating-card {
        animation: vibrate 0.6s infinite;
    }

    .urgent-card {
        border: 2px solid #ff4444 !important;
        box-shadow: 0 4px 8px rgba(255, 68, 68, 0.4) !important;
        background-color: #fff5f5 !important;
    }

    @keyframes vibrate {
        0% { transform: translateX(0); }
        25% { transform: translateX(-1.5px); }
        50% { transform: translateX(1.5px); }
        75% { transform: translateX(-1.5px); }
        100% { transform: translateX(0); }
    }

    .kanban-card-resolvido {
        border-left-color: #28a745;
        background-color: #f8fff8;
    }
    .kanban-card-fechado {
        border-left-color: #17a2b8;
        background-color: #f0fcff;
    }
    .kanban-card-cancelado {
        border-left-color: #dc3545;
        background-color: #fff5f5;
    }
    .kanban-card-em-andamento {
        border-left-color: #007bff;
        background-color: #f0f8ff;
    }
    .kanban-card-designado {
        border-left-color: #6f42c1;
        background-color: #f8f5ff;
    }
    .kanban-card-pendente {
        border-left-color: #ffc107;
        background-color: #fffbf0;
    }
    .kanban-card-pausa {
        border-left-color: #fd7e14;
        background-color: #fff5f0;
    }
    .kanban-card-outros {
        border-left-color: #6c757d;
        background-color: #f8f9fa;
    }
    .day-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        text-align: center;
        font-weight: bold;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .current-week-header {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 15px;
        text-align: center;
        font-weight: bold;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .show-more-btn {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.8rem;
        margin-top: 5px;
        width: 100%;
    }
    .show-more-btn:hover {
        background-color: #0056b3;
    }
    </style>
    """, unsafe_allow_html=True)