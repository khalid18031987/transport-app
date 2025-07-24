import streamlit as st
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
from datetime import datetime

# =============================
# 🔐 Chargement des variables d'environnement
# =============================
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Valeur par défaut locale

# =============================
# 🔌 Connexion MongoDB avec gestion d'erreur
# =============================
client = None
db = None

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, socketTimeoutMS=20000, connectTimeoutMS=20000)
    client.server_info()  # 💡 Force une exception si le serveur est inaccessible
    db = client["transport_db"]  # Remplace par le nom de ta base
    st.success("✅ Connexion MongoDB réussie.")
except errors.ServerSelectionTimeoutError as err:
    st.error("🚫 Connexion impossible : le cluster MongoDB est hors ligne ou inaccessible.")
    st.warning(f"🛠️ Détail de l'erreur :\n{err}")
    db = None
except Exception as e:
    st.error("🚫 Une erreur inattendue est survenue lors de la connexion à MongoDB.")
    st.warning(str(e))
    db = None

# =============================
# 🚀 App principale
# =============================
st.title("📦 Système de Gestion de Transport")

if db is not None:
    st.info("📡 Mode connecté : lecture depuis MongoDB")
    try:
        produits = list(db.produits.find())  # collection 'produits'
        if produits:
            st.subheader("🧾 Liste des produits")
            for p in produits:
                st.markdown(f"🔹 **{p.get('nom', 'Sans nom')}** - {p.get('prix', '0')}€ (Stock: {p.get('stock', '0')})")
        else:
            st.warning("📭 Aucun produit trouvé dans la base.")
    except Exception as e:
        st.error("❌ Une erreur est survenue lors de la lecture des produits.")
        st.text(str(e))
else:
    st.warning("📴 L’application fonctionne en **mode déconnecté**. Veuillez vérifier le serveur MongoDB.")

# Bonus : affichage date/heure
st.caption(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
