import streamlit as st
import base64

def create_footer():
    """Cria o rodapé da aplicação com logo"""
    logo_path = "Grupo.svg.png"
    
    try:
        # Converter imagem para base64 para usar no HTML
        with open(logo_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
            
        st.markdown(f"""
        <div class="footer">
            <img src="data:image/png;base64,{img_base64}" class="footer-logo" alt="Logo">
            <p class="footer-text"> Desenvolvido por <strong>Júlia Alves Santos </strong></p>
        </div>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        # Fallback caso a imagem não seja encontrada
        st.markdown("""
        <div class="footer">
            <p class="footer-text"> Desenvolvido por <strong>Júlia Alves Santos | GEAT</strong></p>
        </div>
        """, unsafe_allow_html=True)