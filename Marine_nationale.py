import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import re

# Hardcoder la clé API
GOOGLE_API_KEY = "AIzaSyC4LgW7iKhFDH0nl9gL5IfUtGS34oY1_wk"  # Remplacez par votre clé API
genai.configure(api_key=GOOGLE_API_KEY)

# Style personnalisé avec les couleurs de la France
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0055A4 0%, #FFFFFF 50%, #EF4135 100%);
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0.5);
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h1, h2, h3, h4, h5, h6 {
    color: #0055A4;
}

.stButton button {
    background-color: #0055A4;
    color: white;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
    border: 2px solid #EF4135;
}

.stTextInput input {
    border-radius: 5px;
    padding: 10px;
    border: 2px solid #0055A4;
}

.stMarkdown {
    background: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    border: 2px solid #EF4135;
}

.maxime {
    background: linear-gradient(135deg, #0055A4 0%, #EF4135 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Titre et description
st.title("🚢 Chatbot Expert en Stratégies Navales")
st.write("Bienvenue sur ce chatbot expert en stratégie navale française. Posez vos questions pour obtenir des réponses précises et contextuelles !")

# Afficher la maxime
st.markdown(
    """
    <div class="maxime">
        Honneur, Patrie, Valeur, Discipline
    </div>
    """,
    unsafe_allow_html=True,
)

# Barre latérale
with st.sidebar:
    st.header("⚙️ Paramètres")
    temperature = st.slider("Température du modèle", 0.0, 1.0, 0.7)
    max_tokens = st.slider("Nombre maximum de tokens", 100, 2048, 512)
    st.markdown("---")
    st.write("ℹ️ Posez des questions sur les stratégies navales françaises.")

# Liste des modèles disponibles
models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
selected_model_name = st.selectbox("Choisissez un modèle", models)

# Fonction pour extraire des données structurées depuis une réponse
def extract_structured_data(response_text):
    """
    Cherche des informations structurées dans le texte, telles que :
    - Des paires clé-valeur (format : Clé: Valeur)
    - Des nombres ou catégories détectées
    """
    data = []
    # Regex pour trouver des paires clé-valeur
    matches = re.findall(r"([a-zA-ZÀ-ÿ ]+):\s*(\d+)", response_text)
    for match in matches:
        key, value = match
        data.append({"Catégorie": key.strip(), "Valeur": int(value)})
    return data

# Initialisation du chatbot
if selected_model_name:
    model = genai.GenerativeModel(selected_model_name)
    system_prompt = (
        "Tu es un spécialiste de l'histoire des stratégies navales ayant travaillé dans la marine française. "
        "Tu donnes des réponses précises en les replaçant dans le contexte politique du pays. "
        "Si pertinent, inclut des données sous forme structurée (par exemple : \"Catégorie: Valeur\")."
    )
    chat = model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}])

    st.subheader("💬 Discussion")
    user_message = st.text_input("Votre question (écrivez 'fin' pour terminer) :")

    if user_message:
        if user_message.lower() == "fin":
            st.write("Merci et bonne journée !")
        else:
            # Réponse du chatbot
            response = chat.send_message(user_message)
            st.markdown(
                f"""
                <div style="
                    background: rgba(255, 255, 255, 0.9);
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                    border: 2px solid #0055A4;
                ">
                    {response.text}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Extraction de données structurées
            extracted_data = extract_structured_data(response.text)

            if extracted_data:
                # Création d'un dataframe à partir des données extraites
                df = pd.DataFrame(extracted_data)

                # Création d'un graphique
                st.subheader("📊 Visualisation des données extraites")
                fig, ax = plt.subplots()
                ax.bar(df["Catégorie"], df["Valeur"], color="#0055A4")
                ax.set_title("Graphique basé sur les réponses du chatbot", fontsize=14)
                ax.set_xlabel("Catégories", fontsize=12)
                ax.set_ylabel("Valeurs", fontsize=12)
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # Affichage des données brutes
                st.subheader("📄 Données extraites")
                st.dataframe(df)
            else:
                st.write("Aucune donnée structurée n'a été détectée dans la réponse.")