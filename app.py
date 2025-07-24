import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Chargement des variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION")

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Configuration de la page
st.set_page_config(page_title="Produits - Système de Transport", page_icon="📦", layout="wide")

# Catégories disponibles
categories = [
    "Ticket simple", "Abonnement mensuel", "Carte rechargeable", "Carte étudiant",
    "Réservation VIP", "Assistance bagage", "QR Code voyage", "Recharge carte",
    "Crédits de trajet", "Abonnement élève", "Badge bus scolaire",
    "Carte entreprise", "Badge chauffeur", "autre"
]

# Titre principal
st.title("📦 Gestion des Produits")

# Onglets
tabs = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer", "🔍 Filtrer"])

# Onglet : Affichage
with tabs[0]:
    st.subheader("📋 Tous les produits")
    produits = list(collection.find())
    if produits:
        st.success(f"{len(produits)} produits trouvés")
        for p in produits:
            with st.expander(f"{p['nom']} - {p['prix']} DH (Stock: {p['stock']})"):
                st.json(p)
    else:
        st.info("Aucun produit trouvé.")

# Onglet : Ajout
with tabs[1]:
    st.subheader("➕ Ajouter un produit")
    with st.form("form_ajouter"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom*")
            description = st.text_area("Description*")
        with col2:
            prix = st.number_input("Prix*", 0.0, step=0.5)
            stock = st.number_input("Stock*", 0, step=1)
            categorie = st.selectbox("Catégorie*", categories)

        submit = st.form_submit_button("Ajouter")
        if submit:
            if nom and description:
                collection.insert_one({
                    "nom": nom,
                    "description": description,
                    "prix": prix,
                    "stock": stock,
                    "categorie": categorie,
                    "popularite": 0,
                    "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Produit ajouté avec succès ✅")
            else:
                st.warning("Tous les champs obligatoires doivent être remplis")

# Onglet : Suppression
with tabs[2]:
    st.subheader("🗑️ Supprimer un produit")
    noms_produits = [p["nom"] for p in collection.find()]
    if noms_produits:
        prod_nom = st.selectbox("Sélectionner le produit à supprimer", noms_produits)
        if st.button("Supprimer"):
            result = collection.delete_one({"nom": prod_nom})
            if result.deleted_count:
                st.success("Produit supprimé ✅")
            else:
                st.error("Erreur lors de la suppression")
    else:
        st.info("Aucun produit à supprimer")

# Onglet : Filtrer
with tabs[3]:
    st.subheader("🔍 Filtrer les produits")
    with st.form("form_filtrer"):
        col1, col2, col3 = st.columns(3)
        with col1:
            categorie = st.selectbox("Catégorie", ["Toutes"] + categories)
        with col2:
            prix_min = st.number_input("Prix min", 0.0)
            prix_max = st.number_input("Prix max", 1000.0)
        with col3:
            popularite_min = st.number_input("Popularité min", 0)
            stock_min = st.number_input("Stock min", 0)

        submit = st.form_submit_button("Filtrer")
        if submit:
            query = {}
            if categorie != "Toutes":
                query["categorie"] = categorie
            query["prix"] = {"$gte": prix_min, "$lte": prix_max}
            query["popularite"] = {"$gte": popularite_min}
            query["stock"] = {"$gte": stock_min}

            resultats = list(collection.find(query))
            if resultats:
                st.success(f"{len(resultats)} produits correspondent aux filtres")
                for p in resultats:
                    with st.expander(f"{p['nom']} - {p['prix']} DH"):
                        st.json(p)
            else:
                st.warning("Aucun produit ne correspond à ces critères.")
