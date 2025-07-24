import streamlit as st
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
from datetime import datetime

# =============================
# === CONFIGURATION INITIALE ===
# =============================

load_dotenv()  # Charge les variables d'environnement depuis un fichier .env

MONGO_URI = os.getenv("MONGO_URI")  # Assurez-vous que cette variable est bien définie
DB_NAME = "TransportProject"
COLLECTION_NAME = "Produits"

st.title("🛠️ Connexion MongoDB avec gestion d'erreurs")

# ==============================
# === FONCTION DE CONNEXION ===
# ==============================

@st.cache_resource
def connect_to_mongo(uri):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        # Force une requête pour tester la connexion (ping)
        client.admin.command("ping")
        st.success("✅ Connexion à MongoDB réussie")
        return client
    except errors.ServerSelectionTimeoutError as e:
        st.error("🚫 Échec de la connexion : Cluster MongoDB hors ligne ou inaccessible.")
        st.code(str(e), language="bash")
        return None
    except Exception as e:
        st.error("❌ Une erreur inattendue est survenue lors de la connexion.")
        st.code(str(e), language="bash")
        return None

# ===================================
# === UTILISATION DE LA CONNEXION ===
# ===================================

client = connect_to_mongo(MONGO_URI)

if client:
    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        produits = list(collection.find())

        if produits:
            st.subheader("📦 Produits dans la base de données :")
            for produit in produits:
                st.write(f"🔹 {produit.get('nom', 'Inconnu')} - {produit.get('prix', '?')}€ (Stock: {produit.get('stock', 0)})")
        else:
            st.warning("🟡 Aucun produit trouvé dans la collection.")
    except Exception as e:
        st.error("❌ Erreur lors de la récupération des données depuis MongoDB.")
        st.code(str(e), language="bash")
