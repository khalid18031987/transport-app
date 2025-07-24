import streamlit as st
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
from datetime import datetime

# ===========================
# === CONFIGURATION STREAMLIT
# ===========================
st.set_page_config(page_title="Système de Gestion de Transport", page_icon="📦")

# ===========================
# === PARAMÈTRES MONGODB
# ===========================
MONGODB_URI = "mongodb+srv://mk18031987:UCyuhDG6l94OWXSl@cluster0.nw84anp.mongodb.net/transportdb?retryWrites=true&w=majority"
MONGO_DB = "transportdb"

MONGO_COLLECTION = "produits"
MONGO_COLLECTION_UTILISATEURS = "utilisateurs"
MONGO_COLLECTION_PANIERS = "paniers"
MONGO_COLLECTION_COMMANDES = "commandes"
MONGO_COLLECTION_AVIS = "avis"

# ===========================
# === FONCTION DE CONNEXION
# ===========================
def connect_to_mongodb():
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force la connexion pour déclencher une exception si échoue
        db = client[MONGO_DB]
        st.success("✅ Connexion MongoDB réussie.")
        return db
    except errors.ServerSelectionTimeoutError as err:
        st.error("🚫 Connexion impossible : le cluster MongoDB est hors ligne ou inaccessible.")
        st.warning(f"🛠️ Détail de l'erreur : {err}")
        return None
    except Exception as e:
        st.error("🚫 Une erreur inattendue est survenue lors de la connexion à MongoDB.")
        st.warning(f"🛠️ Détail de l'erreur : {e}")
        return None

# ===========================
# === CONNEXION À MONGODB
# ===========================
db = connect_to_mongodb()

# ===========================
# === INTERFACE PRINCIPALE
# ===========================
st.markdown("## 📦 Système de Gestion de Transport")

if db is not None:
    st.success("🟢 Mode connecté à MongoDB")
    produits_col = db[MONGO_COLLECTION]
    utilisateurs_col = db[MONGO_COLLECTION_UTILISATEURS]
    paniers_col = db[MONGO_COLLECTION_PANIERS]
    commandes_col = db[MONGO_COLLECTION_COMMANDES]
    avis_col = db[MONGO_COLLECTION_AVIS]

    # Exemple : afficher le nombre de produits
    nb_produits = produits_col.count_documents({})
    st.info(f"🔍 Produits disponibles : **{nb_produits}**")
else:
    st.warning("📴 L’application fonctionne en mode déconnecté. Veuillez vérifier le serveur MongoDB.")
    st.write(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
