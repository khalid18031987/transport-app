import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from datetime import datetime

# ======================================
# 🔧 CONFIGURATION DE LA CONNEXION MONGO
# ======================================

MONGODB_URI = "mongodb+srv://mk18031987:UCyuhDG6l94OWXSl@cluster0.nw84anp.mongodb.net/transportdb?retryWrites=true&w=majority"
MONGO_DB = "transportdb"

MONGO_COLLECTION = "produits"
MONGO_COLLECTION_UTILISATEURS = "utilisateurs"
MONGO_COLLECTION_PANIERS = "paniers"
MONGO_COLLECTION_COMMANDES = "commandes"
MONGO_COLLECTION_AVIS = "avis"

# Fonction de connexion MongoDB avec gestion d’erreurs
@st.cache_resource
def init_connection():
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force la connexion pour attraper les erreurs
        db = client[MONGO_DB]
        st.success("✅ Connexion MongoDB réussie.")
        return db
    except (ConnectionFailure, ConfigurationError) as e:
        st.error("🚫 Connexion impossible : le cluster MongoDB est hors ligne ou inaccessible.")
        st.markdown(f"🛠️ Détail de l'erreur : `{e}`")
        st.warning("📴 L’application fonctionne en mode déconnecté. Veuillez vérifier le serveur MongoDB.")
        return None

db = init_connection()

# ======================================
# 🖼️ INTERFACE STREAMLIT (exemple simple)
# ======================================

st.title("📦 Système de Gestion de Transport")

if db:
    produits_collection = db[MONGO_COLLECTION]
    utilisateurs_collection = db[MONGO_COLLECTION_UTILISATEURS]
    paniers_collection = db[MONGO_COLLECTION_PANIERS]
    commandes_collection = db[MONGO_COLLECTION_COMMANDES]
    avis_collection = db[MONGO_COLLECTION_AVIS]

    st.header("🔍 Produits disponibles")
    produits = list(produits_collection.find())
    
    if produits:
        for produit in produits:
            st.write(f"🔹 {produit.get('nom', 'Sans nom')} - {produit.get('prix', 0)}€ (Stock: {produit.get('stock', 0)})")
    else:
        st.info("Aucun produit trouvé.")
else:
    st.stop()
