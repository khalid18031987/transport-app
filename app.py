import streamlit as st
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def connect_to_mongodb(uri):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Tester la connexion avec un ping
        client.admin.command("ping")
        return client
    except errors.ServerSelectionTimeoutError as err:
        st.error("🚫 Connexion impossible : le cluster MongoDB est hors ligne ou inaccessible.")
        st.error(f"Détail de l'erreur : {err}")
        return None
    except errors.ConnectionFailure as err:
        st.error("❌ Échec de connexion à MongoDB.")
        st.error(f"Détail : {err}")
        return None
    except Exception as e:
        st.error("❗ Une erreur inattendue est survenue.")
        st.error(f"Détail : {e}")
        return None

# Connexion
client = connect_to_mongodb(MONGO_URI)

# Utilisation de la base de données si la connexion est réussie
if client is not None:
    db = client["transport_db"]
    st.success("✅ Connexion réussie à MongoDB Atlas.")
else:
    db = None
    st.warning("🔌 Aucune connexion à MongoDB.")
