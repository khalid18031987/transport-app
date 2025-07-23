import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from bson.objectid import ObjectId
from PIL import Image
import numpy as np
import logging
from pymongo.errors import PyMongoError

# ==============================================
# === CONFIGURATION INITIALE ET CONNEXION DB ===
# ==============================================

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fonction pour initialiser la connexion MongoDB
@st.cache_resource
def init_db_connection():
    """Initialise et cache la connexion MongoDB"""
    try:
        # Charge les variables d'environnement selon le contexte
        if st.secrets.get("MONGO_URI"):  # Production (Streamlit Cloud)
            MONGO_URI = st.secrets["MONGO_URI"]
            DB_NAME = st.secrets["MONGO_DB"]
            COLLECTION_NAME = st.secrets.get("MONGO_COLLECTION", "products")
            COLLECTION_USERS = st.secrets.get("MONGO_COLLECTION_UTILISATEURS", "users")
            COLLECTION_CARTS = st.secrets.get("MONGO_COLLECTION_PANIERS", "carts")
            COLLECTION_ORDERS = st.secrets.get("MONGO_COLLECTION_COMMANDES", "orders")
            COLLECTION_REVIEWS = st.secrets.get("MONGO_COLLECTION_AVIS", "reviews")
        else:                            # Développement local
            load_dotenv()
            MONGO_URI = os.getenv("MONGO_URI")
            DB_NAME = os.getenv("MONGO_DB")
            COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "products")
            COLLECTION_USERS = os.getenv("MONGO_COLLECTION_UTILISATEURS", "users")
            COLLECTION_CARTS = os.getenv("MONGO_COLLECTION_PANIERS", "carts")
            COLLECTION_ORDERS = os.getenv("MONGO_COLLECTION_COMMANDES", "orders")
            COLLECTION_REVIEWS = os.getenv("MONGO_COLLECTION_AVIS", "reviews")

        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            tls=True,
            retryWrites=True,
            w="majority",
            appname="Streamlit_Transport_App"
        )
        
        # Test de connexion
        client.admin.command('ping')
        logger.info("Connexion MongoDB établie avec succès")
        
        db = client[DB_NAME]
        return {
            'client': client,
            'db': db,
            'products': db[COLLECTION_NAME],
            'users': db[COLLECTION_USERS],
            'carts': db[COLLECTION_CARTS],
            'orders': db[COLLECTION_ORDERS],
            'reviews': db[COLLECTION_REVIEWS]
        }
        
    except Exception as e:
        logger.error(f"Erreur de connexion MongoDB : {str(e)}")
        st.error(f"""
        ❌ Connexion à la base de données échouée :
        {str(e)}
        
        Vérifiez que :
        1. Votre URI MongoDB est correcte
        2. L'IP 0.0.0.0/0 est autorisée dans MongoDB Atlas
        3. Vos identifiants sont valides
        """)
        st.stop()

# Initialisation de la connexion
db_connection = init_db_connection()
products_col = db_connection['products']
users_col = db_connection['users']
carts_col = db_connection['carts']
orders_col = db_connection['orders']
reviews_col = db_connection['reviews']

# ==============================================
# === FONCTIONS UTILITAIRES ET VALIDATION ======
# ==============================================

def validate_product_data(nom: str, prix: float, stock: int, description: str) -> bool:
    """Valide les données d'un produit avant insertion"""
    if not nom or len(nom.strip()) < 2:
        raise ValueError("Le nom doit contenir au moins 2 caractères")
    if prix <= 0:
        raise ValueError("Le prix doit être positif")
    if stock < 0:
        raise ValueError("Le stock ne peut pas être négatif")
    if not description or len(description.strip()) < 10:
        raise ValueError("La description doit contenir au moins 10 caractères")
    return True

def validate_user_data(nom: str, email: str, adresse: str) -> bool:
    """Valide les données utilisateur"""
    if not nom or len(nom.strip()) < 2:
        raise ValueError("Nom invalide")
    if "@" not in email or "." not in email:
        raise ValueError("Email invalide")
    if not adresse or len(adresse.strip()) < 5:
        raise ValueError("Adresse invalide")
    return True

def safe_object_id(id_str: str) -> ObjectId:
    """Convertit une chaîne en ObjectId de manière sécurisée"""
    try:
        return ObjectId(id_str)
    except Exception as e:
        logger.error(f"ID invalide : {id_str} - {str(e)}")
        raise ValueError("Identifiant invalide")

# ==============================================
# === INTERFACE STREAMLIT ======================
# ==============================================

# Configuration de la page
st.set_page_config(
    page_title="Gestion d'un Système de Transport", 
    layout="wide",
    page_icon="🚍"
)

# CSS personnalisé
st.markdown("""
<style>
    :root {
        --primary: #4361ee;
        --secondary: #3f37c9;
        --accent: #4895ef;
        --light: #f8f9fa;
        --dark: #212529;
        --success: #4cc9f0;
        --warning: #f72585;
    }
    
    /* Style général */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f5f7fa;
    }
    
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 4px solid var(--primary);
    }
    
    .section-title {
        color: var(--dark);
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        padding-bottom: 0.5rem;
    }
    
    .section-title:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
    }
</style>
""", unsafe_allow_html=True)

# En-tête avec image
try:
    image = Image.open("transport.png")
    st.image(np.array(image), use_container_width=True)
except FileNotFoundError:
    st.warning("Image d'en-tête non trouvée")

# Catégories de produits
categories = [
    "Ticket simple", "Abonnement mensuel", "Carte rechargeable", 
    "Carte étudiant", "Réservation VIP", "Assistance bagage",
    "QR Code voyage", "Recharge carte", "Crédits de trajet",
    "Abonnement élève", "Badge bus scolaire", "Carte entreprise",
    "Badge chauffeur", "autre"
]

# ==============================================
# === STRUCTURE PRINCIPALE =====================
# ==============================================

tabs = st.tabs(["📦 Produits", "👥 Utilisateurs", "🛒 Paniers", "📋 Commandes", "⭐ Avis"])

# Onglet Produits
with tabs[0]:
    st.markdown('<div class="section-title">Gestion des produits</div>', unsafe_allow_html=True)
    prod_tabs = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer", "🔍 Filtrer"])
    
    with prod_tabs[0]:  # Affichage
        try:
            produits = list(products_col.find().max_time_ms(3000))
            if produits:
                st.success(f"📊 {len(produits)} produits trouvés")
                for p in produits:
                    with st.expander(f"🔹 {p['nom']} - {p['prix']}DH (Stock: {p.get('stock', 0)})"):
                        st.json(p)
            else:
                st.info("Aucun produit trouvé")
        except PyMongoError as e:
            st.error(f"Erreur de base de données : {str(e)}")
    
    with prod_tabs[1]:  # Ajout
        with st.form("ajouter_produit", clear_on_submit=True):
            cols = st.columns(2)
            with cols[0]:
                nom = st.text_input("Nom du produit*")
                description = st.text_area("Description*")
            with cols[1]:
                prix = st.number_input("Prix*", min_value=0.0, step=0.5)
                stock = st.number_input("Stock*", min_value=0)
                categorie = st.selectbox("Catégorie*", categories)
            
            if st.form_submit_button("➕ Ajouter produit"):
                try:
                    validate_product_data(nom, prix, stock, description)
                    product_data = {
                        "nom": nom,
                        "description": description,
                        "prix": prix,
                        "stock": stock,
                        "categorie": categorie,
                        "popularite": 0,
                        "date_creation": datetime.now()
                    }
                    products_col.insert_one(product_data)
                    st.success("Produit ajouté avec succès ✅")
                except ValueError as e:
                    st.error(str(e))
                except PyMongoError as e:
                    st.error(f"Erreur DB : {str(e)}")

    with prod_tabs[2]:  # Suppression
        with st.form("supprimer_produit"):
            try:
                produits_liste = [p["nom"] for p in products_col.find({}, {"nom": 1})]
                produit = st.selectbox("Sélectionner un produit à supprimer", produits_liste)
                
                if st.form_submit_button("🗑️ Supprimer"):
                    result = products_col.delete_one({"nom": produit})
                    if result.deleted_count:
                        st.success("Produit supprimé avec succès ✅")
                    else:
                        st.warning("Produit non trouvé")
            except PyMongoError as e:
                st.error(f"Erreur DB : {str(e)}")

    with prod_tabs[3]:  # Filtrage
        with st.form("filtrer_produits"):
            cols = st.columns(3)
            with cols[0]:
                categorie = st.selectbox("Catégorie", ["Toutes"] + categories)
            with cols[1]:
                prix_min = st.number_input("Prix minimum", 0.0, 1000.0, 0.0)
                prix_max = st.number_input("Prix maximum", 0.0, 1000.0, 1000.0)
            with cols[2]:
                pop_min = st.number_input("Popularité minimum", 0, 100, 0)
                stock_min = st.number_input("Stock minimum", 0, 1000, 0)
            
            if st.form_submit_button("🔍 Appliquer les filtres"):
                try:
                    query = {"prix": {"$gte": prix_min, "$lte": prix_max}}
                    if categorie != "Toutes":
                        query["categorie"] = categorie
                    if pop_min > 0:
                        query["popularite"] = {"$gte": pop_min}
                    if stock_min > 0:
                        query["stock"] = {"$gte": stock_min}
                    
                    produits = list(products_col.find(query).max_time_ms(3000))
                    if produits:
                        st.success(f"🔎 {len(produits)} produits trouvés")
                        for p in produits:
                            with st.expander(f"{p['nom']} - {p['prix']}DH"):
                                st.json(p)
                    else:
                        st.warning("Aucun produit ne correspond aux critères")
                except PyMongoError as e:
                    st.error(f"Erreur DB : {str(e)}")

# Onglet Utilisateurs (structure similaire)
with tabs[1]:
    st.markdown('<div class="section-title">Gestion des utilisateurs</div>', unsafe_allow_html=True)
    user_tabs = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])
    
    # ... (Code similaire pour la gestion des utilisateurs)

# Onglet Paniers (structure similaire)
with tabs[2]:
    st.markdown('<div class="section-title">Gestion des paniers</div>', unsafe_allow_html=True)
    cart_tabs = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])
    
    # ... (Code similaire pour la gestion des paniers)

# Onglet Commandes (structure similaire)
with tabs[3]:
    st.markdown('<div class="section-title">Gestion des commandes</div>', unsafe_allow_html=True)
    order_tabs = st.tabs(["📋 Afficher", "➕ Créer", "🗑️ Supprimer"])
    
    # ... (Code similaire pour la gestion des commandes)

# Onglet Avis (structure similaire)
with tabs[4]:
    st.markdown('<div class="section-title">Gestion des avis</div>', unsafe_allow_html=True)
    review_tabs = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])
    
    # ... (Code similaire pour la gestion des avis)

# ==============================================
# === PIED DE PAGE =============================
# ==============================================

st.markdown("""
<div style="margin-top: 50px; padding: 20px; background: linear-gradient(135deg, #4361ee, #3f37c9); color: white; border-radius: 10px;">
    <table style="width: 100%;">
        <tr>
            <td style="text-align: left; width: 49%;">
                <p><strong>Encadré par :</strong><br>
                Pr S.CHERDAL<br>
                Mme Noussaiba Daali</p>
            </td>
            <td style="width: 1px; background-color: white; border-radius: 10px;"></td>
            <td style="text-align: left; width: 49%;">
                <p><strong>Réalisé par :</strong><br>
                EL MOUTAOUAKIL Khalid<br>
                HAMOUDAN Badreddine</p>
            </td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)
