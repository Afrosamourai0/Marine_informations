import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import re

# Clé API (hardcodée)
GOOGLE_API_KEY = "AIzaSyC4LgW7iKhFDH0nl9gL5IfUtGS34oY1_wk"
genai.configure(api_key=GOOGLE_API_KEY)

# Style personnalisé
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0055A4 0%, #FFFFFF 50%, #EF4135 100%);
    background-size: cover;
}
.stButton button {
    background-color: #0055A4;
    color: white;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
    border: 2px solid #EF4135;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Titre et description
st.title("🚢 Chatbot Expert en Stratégies Navales")
st.write("Posez vos questions sur la stratégie navale française.")

# Paramètres dans la barre latérale
with st.sidebar:
    st.header("⚙️ Paramètres")
    temperature = st.slider("Température du modèle", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Nombre maximum de tokens", 100, 2048, 512)

# Liste des modèles disponibles
try:
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    selected_model_name = st.selectbox("Choisissez un modèle", models)
except Exception as e:
    st.error(f"Erreur de récupération des modèles : {e}")
    selected_model_name = None

# Fonction d'extraction de données structurées
def extract_structured_data(response_text):
    """Extrait les paires clé-valeur du texte."""
    data = re.findall(r"([a-zA-ZÀ-ÿ ]+):\s*(\d+)", response_text)
    return [{"Catégorie": key.strip(), "Valeur": int(value)} for key, value in data]

# Initialisation du modèle et du chatbot
if selected_model_name:
    model = genai.GenerativeModel(selected_model_name)
    chat = model.start_chat(history=[])

    st.subheader("💬 Discussion")

    # Interface avec bouton d'envoi
    user_message = st.text_input("Votre question :", key="user_input")
    if st.button("Envoyer") and user_message:
        with st.chat_message("user"):
            st.write(user_message)

        try:
            response = chat.send_message(user_message)
            with st.chat_message("assistant"):
                st.markdown(response.text)

            # Extraction et affichage des données
            extracted_data = extract_structured_data(response.text)
            if extracted_data:
                df = pd.DataFrame(extracted_data)
                st.subheader("📊 Données extraites")
                fig, ax = plt.subplots()
                ax.bar(df["Catégorie"], df["Valeur"], color="#0055A4")
                ax.set_title("Données extraites du chatbot")
                ax.set_xlabel("Catégories")
                ax.set_ylabel("Valeurs")
                plt.xticks(rotation=45)
                st.pyplot(fig)
                st.dataframe(df)
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")
