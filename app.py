import streamlit as st
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os

# ==========================================
# 🔧 Chargement des variables d’environnement
# ==========================================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# ==========================================
# 🔌 Connexion MongoDB avec gestion d’erreurs
# ==========================================
client = None
db = None
connected = False

try:
    # Timeout plus rapide pour test local
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Tentative de connexion
    client.admin.command('ping')

    db = client['transport']  # Remplacez 'transport' par le nom de votre base
    connected = True

except errors.ServerSelectionTimeoutError as e:
    st.error("🚫 Connexion impossible : le cluster MongoDB est hors ligne ou inaccessible.")
    st.text(f"Détail : {e}")
except errors.ConnectionFailure as e:
    st.error("🔌 Échec de la connexion à MongoDB.")
    st.text(f"Détail : {e}")
except Exception as e:
    st.error("❌ Une erreur inattendue est survenue lors de la connexion à MongoDB.")
    st.text(f"Détail : {e}")

# ==========================================
# ✅ Utilisation si connecté
# ==========================================
if connected and db is not None:
    st.success("✅ Connexion MongoDB réussie.")
    # Exemple d'affichage de collections
    st.write("Collections disponibles :", db.list_collection_names())
else:
    st.warning("🛠️ L’application fonctionne en mode déconnecté.")
