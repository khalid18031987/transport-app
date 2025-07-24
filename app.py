import streamlit as st
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
from datetime import datetime
from bson.objectid import ObjectId
from PIL import Image
import numpy as np

# ==============================================
# === CONFIGURATION INITIALE ET CONNEXION DB ===
# ==============================================

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration MongoDB avec fallback
MONGODB_URI = os.getenv("MONGO_URI", "mongodb+srv://mk18031987:UCyuhDG6l94OWXSl@cluster0.nw84anp.mongodb.net/transportdb?retryWrites=true&w=majority")
MONGO_DB = os.getenv("MONGO_DB", "transportdb")

# Noms des collections
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "produits")
MONGO_COLLECTION_UTILISATEURS = os.getenv("MONGO_COLLECTION_UTILISATEURS", "utilisateurs")
MONGO_COLLECTION_PANIERS = os.getenv("MONGO_COLLECTION_PANIERS", "paniers")
MONGO_COLLECTION_COMMANDES = os.getenv("MONGO_COLLECTION_COMMANDES", "commandes")
MONGO_COLLECTION_AVIS = os.getenv("MONGO_COLLECTION_AVIS", "avis")

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

# Initialisation des collections
if db is not None:
    collection = db[MONGO_COLLECTION]
    collection_users = db[MONGO_COLLECTION_UTILISATEURS]
    collection_paniers = db[MONGO_COLLECTION_PANIERS]
    collection_commandes = db[MONGO_COLLECTION_COMMANDES]
    collection_avis = db[MONGO_COLLECTION_AVIS]
else:
    # Mode déconnecté - initialisation des variables pour éviter les erreurs
    collection = None
    collection_users = None
    collection_paniers = None
    collection_commandes = None
    collection_avis = None

# ==============================================
# === CONFIGURATION DE L'INTERFACE STREAMLIT ===
# ==============================================

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Gestion d'un Système de Transport", 
    layout="wide",  # Layout large pour utiliser tout l'espace
    page_icon="🚍"  # Icône de bus
)

# CSS personnalisé pour améliorer l'interface
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
    
    /* Style pour l'image d'en-tête */
    .stImage {
        border-radius: 0 0 20px 20px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .stImage img {
        object-fit: cover;
        width: 100%;
        max-height: 300px;
    }
    
    /* Onglets */
    .stTabs [role="tablist"] {
        gap: 10px;
        margin-bottom: 1.5rem;
    }
    
    .stTabs [role="tab"] {
        background: white;
        color: var(--dark);
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(67, 97, 238, 0.2);
    }
    
    .stTabs [role="tab"]:hover {
        background: #f1f3ff;
        color: var(--primary);
    }
    
    /* Cartes */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 4px solid var(--primary);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .card-title {
        color: var(--primary);
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(67, 97, 238, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, var(--secondary), var(--primary));
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(67, 97, 238, 0.4);
        color: white;
    }
    
    /* Inputs */
    .stTextInput>div>div>input, 
    .stTextArea>div>textarea,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>div {
        border-radius: 8px !important;
        border: 1px solid #e9ecef !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stTextInput>div>div>input:focus, 
    .stTextArea>div>textarea:focus,
    .stNumberInput>div>div>input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2) !important;
    }
    
    /* JSON display */
    .stJson {
        background: #f8f9fa !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        border-left: 4px solid var(--accent) !important;
    }
    
    /* Sections */
    .section {
        margin-bottom: 2.5rem;
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
        border-radius: 2px;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .stTabs [role="tab"] {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
    }
    
    /* Message de statut */
    .connection-status {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .connected {
        background-color: #d4edda;
        color: #155724;
    }
    .disconnected {
        background-color: #f8d7da;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================
# === ELEMENTS VISUELS ET FONCTIONS UTILITAIRES =
# ==============================================

# En-tête avec image
try:
    # Tentative de chargement de l'image d'en-tête
    image = Image.open("transport.png")
    image_array = np.array(image)
    st.image(image_array, use_container_width=True, 
             output_format="PNG")
except FileNotFoundError:
    # Fallback si l'image n'est pas trouvée
    st.error("L'image transport.png est introuvable. Veuillez placer l'image dans le même répertoire que ce script.")
    st.image("https://via.placeholder.com/1200x300?text=Transport+System", use_container_width=True)

# Catégories de produits disponibles
categories = [
    "Ticket simple", "Abonnement mensuel", "Carte rechargeable", "Carte étudiant",
    "Réservation VIP", "Assistance bagage", "QR Code voyage", "Recharge carte",
    "Crédits de trajet", "Abonnement élève", "Badge bus scolaire",
    "Carte entreprise", "Badge chauffeur", "autre"
]

# Fonction utilitaire pour créer des sections avec titre stylisé
def create_section(title):
    st.markdown(f'<div class="section"><div class="section-title">{title}</div>', unsafe_allow_html=True)

# Fonction pour vérifier la connexion avant les opérations MongoDB
def check_connection():
    if db is None:
        st.warning("⚠️ L'application est en mode déconnecté. Les opérations ne seront pas enregistrées.")
        return False
    return True

# ==============================================
# === STRUCTURE PRINCIPALE DE L'APPLICATION ====
# ==============================================

# Affichage du statut de connexion
if db is not None:
    st.markdown('<div class="connection-status connected">🟢 Connecté à MongoDB</div>', unsafe_allow_html=True)
    nb_produits = collection.count_documents({}) if collection is not None else 0
    st.info(f"🔍 Produits disponibles : **{nb_produits}**")
else:
    st.markdown('<div class="connection-status disconnected">🔴 Mode déconnecté - Vérifiez la connexion MongoDB</div>', unsafe_allow_html=True)
    st.write(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Création des onglets principaux
tabs = st.tabs(["📦 Produits", "👥 Utilisateurs", "🛒 Paniers", "📋 Commandes", "⭐ Avis"])

# ====================
# ==== PRODUITS ======
# ====================
with tabs[0]:
    create_section("Gestion des produits")
    # Sous-onglets pour les produits
    prod_tab = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer", "🔍 Filtrer"])

    # 1. Affichage des produits
    with prod_tab[0]:
        if check_connection():
            produits = list(collection.find()) if collection is not None else []
            if produits:
                st.success(f"📊 {len(produits)} produits trouvés")
                for p in produits:
                    # Affiche chaque produit dans un expander avec ses détails
                    with st.expander(f"🔹 {p['nom']} - {p['prix']}DH (Stock: {p['stock']})"):
                        st.json(p)  # Format JSON pour une visualisation claire
            else:
                st.info("Aucun produit trouvé.")

    # 2. Ajout de produit
    with prod_tab[1]:
        with st.form("ajouter_produit"):
            cols = st.columns(2)  # Layout en 2 colonnes
            with cols[0]:
                nom = st.text_input("Nom du produit*", key="prod_aj_nom")
                description = st.text_area("Description*", key="prod_aj_desc")
            with cols[1]:
                prix = st.number_input("Prix*", 0.0, key="prod_aj_prix", step=0.5)
                stock = st.number_input("Stock*", 0, key="prod_aj_stock")
                categorie = st.selectbox("Catégorie*", categories, key="prod_aj_cat")
            
            if st.form_submit_button("➕ Ajouter produit"):
                if not check_connection():
                    st.error("Opération impossible en mode déconnecté")
                else:
                    # Validation des champs obligatoires
                    if nom and description and categorie:
                        collection.insert_one({
                            "nom": nom,
                            "description": description,
                            "prix": prix,
                            "stock": stock,
                            "categorie": categorie,
                            "popularite": 0,  # Popularité initiale à 0
                            "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.success("Produit ajouté avec succès ✅")
                    else:
                        st.warning("Veuillez remplir tous les champs obligatoires (*)")

    # 3. Suppression de produit
    with prod_tab[2]:
        with st.form("supprimer_produit"):
            produits_liste = [p["nom"] for p in collection.find()] if collection is not None else []
            produit = st.selectbox("Sélectionner un produit à supprimer", produits_liste, key="prod_sup_select")
            
            if st.form_submit_button("🗑️ Supprimer"):
                if not check_connection():
                    st.error("Opération impossible en mode déconnecté")
                else:
                    result = collection.delete_one({"nom": produit})
                    if result.deleted_count:
                        st.success("Produit supprimé avec succès ✅")
                    else:
                        st.error("Erreur lors de la suppression")

    # 4. Filtrage des produits
    with prod_tab[3]:
        with st.form("filtrer_produits"):
            cols = st.columns(3)
            with cols[0]:
                categorie = st.selectbox("Catégorie", ["Toutes"] + categories, key="prod_fil_cat")
            with cols[1]:
                prix_min = st.number_input("Prix minimum", 0.0, 1000.0, 0.0, key="prod_fil_prix_min")
                prix_max = st.number_input("Prix maximum", 0.0, 1000.0, 1000.0, key="prod_fil_prix_max")
            with cols[2]:
                pop_min = st.number_input("Popularité minimum", 0, 100, 0, key="prod_fil_pop_min")
                stock_min = st.number_input("Stock minimum", 0, 1000, 0, key="prod_fil_stock_min")
            
            if st.form_submit_button("🔍 Appliquer les filtres"):
                if not check_connection():
                    st.error("Opération impossible en mode déconnecté")
                else:
                    # Construction de la requête MongoDB en fonction des filtres
                    query = {}
                    if categorie != "Toutes":
                        query["categorie"] = categorie
                    query["prix"] = {"$gte": prix_min, "$lte": prix_max}
                    query["popularite"] = {"$gte": pop_min}
                    query["stock"] = {"$gte": stock_min}
                    
                    produits = list(collection.find(query))
                    if produits:
                        st.success(f"🔎 {len(produits)} produits correspondent aux critères")
                        for p in produits:
                            with st.expander(f"{p['nom']} - {p['prix']}DH"):
                                st.json(p)
                    else:
                        st.warning("Aucun produit ne correspond aux critères.")

# =========================
# ==== UTILISATEURS =======
# =========================
with tabs[1]:
    create_section("Gestion des utilisateurs")
    user_tab = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])

    # 1. Affichage des utilisateurs
    with user_tab[0]:
        if check_connection():
            users = list(collection_users.find()) if collection_users else []
            if users:
                st.success(f"👥 {len(users)} utilisateurs trouvés")
                for u in users:
                    with st.expander(f"👤 {u['nom']} - {u['email']}"):
                        st.json(u)
                        # Affichage de l'historique d'achats de l'utilisateur
                        historique = u.get("historique_achats", [])
                        if historique:
                            st.markdown("**📜 Historique d'achats :**")
                            for com_id in historique:
                                com = collection_commandes.find_one({"_id": com_id})
                                if com:
                                    st.json(com)
                        else:
                            st.info("Aucun historique d'achats")
            else:
                st.info("Aucun utilisateur trouvé.")

    # 2. Ajout d'utilisateur
    with user_tab[1]:
        with st.form("ajouter_utilisateur"):
            cols = st.columns(2)
            with cols[0]:
                nom = st.text_input("Nom*", key="user_aj_nom")
                email = st.text_input("Email*", key="user_aj_email")
            with cols[1]:
                adresse = st.text_input("Adresse*", key="user_aj_adresse")
                telephone = st.text_input("Téléphone", key="user_aj_tel")
            
            if st.form_submit_button("➕ Ajouter utilisateur"):
                if not check_connection():
                    st.error("Opération impossible en mode déconnecté")
                else:
                    if nom and email and adresse:
                        # Vérification si l'email existe déjà
                        if collection_users.find_one({"email": email}):
                            st.error("Cet email est déjà utilisé")
                        else:
                            collection_users.insert_one({
                                "nom": nom,
                                "email": email,
                                "adresse": adresse,
                                "telephone": telephone,
                                "date_inscription": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "historique_achats": []  # Initialisation d'un historique vide
                            })
                            st.success("Utilisateur ajouté avec succès ✅")
                    else:
                        st.warning("Veuillez remplir les champs obligatoires (*)")

    # 3. Suppression d'utilisateur
    with user_tab[2]:
        with st.form("supprimer_utilisateur"):
            users_list = [u["email"] for u in collection_users.find()] if collection_users else []
            user_email = st.selectbox("Sélectionner un utilisateur", users_list, key="user_sup_select")
            
            if st.form_submit_button("🗑️ Supprimer"):
                if not check_connection():
                    st.error("Opération impossible en mode déconnecté")
                else:
                    result = collection_users.delete_one({"email": user_email})
                    if result.deleted_count:
                        st.success("Utilisateur supprimé avec succès ✅")
                    else:
                        st.error("Erreur lors de la suppression")

# =====================
# ==== PANIERS ========
# =====================
with tabs[2]:
    create_section("Gestion des paniers")
    panier_tab = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])

    # 1. Affichage des paniers
    with panier_tab[0]:
        if check_connection():
            paniers = list(collection_paniers.find()) if collection_paniers else []
            if paniers:
                st.success(f"🛒 {len(paniers)} paniers trouvés")
                for p in paniers:
                    with st.expander(f"🛍️ Panier de {p['utilisateur']} - Total: {p['total']}DH"):
                        st.json(p)
            else:
                st.info("Aucun panier trouvé.")

    # 2. Ajout de panier
    with panier_tab[1]:
        with st.form("ajouter_panier"):
            utilisateurs = [u["email"] for u in collection_users.find()] if collection_users else []
            if not utilisateurs:
                st.warning("Aucun utilisateur disponible.")
            else:
                utilisateur = st.selectbox("Utilisateur*", utilisateurs, key="panier_aj_utilisateur")
                produits = [p["nom"] for p in collection.find()] if collection else []
                
                st.markdown("**📦 Sélection des produits :**")
                cols = st.columns(2)
                quantites = {}
                for i, produit in enumerate(produits):
                    with cols[i % 2]:
                        qte = st.number_input(
                            f"Quantité pour {produit}",
                            0, 
                            key=f"panier_aj_qte_{produit}",
                            help=f"Stock disponible: {collection.find_one({'nom': produit})['stock'] if collection and collection.find_one({'nom': produit}) else 0}"
                        )
                        if qte > 0:
                            quantites[produit] = qte
                
                if st.form_submit_button("➕ Ajouter panier"):
                    if not check_connection():
                        st.error("Opération impossible en mode déconnecté")
                    else:
                        if utilisateur and quantites:
                            # Calcul du total du panier
                            total = sum(collection.find_one({"nom": p})["prix"] * q for p, q in quantites.items())
                            collection_paniers.insert_one({
                                "utilisateur": utilisateur,
                                "produits": quantites,
                                "total": total,
                                "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.success(f"Panier ajouté avec succès ✅ Total: {total:.2f} DH")
                        else:
                            st.warning("Veuillez sélectionner au moins un produit")

    # 3. Suppression de panier
    with panier_tab[2]:
        with st.form("supprimer_panier"):
            paniers_list = [p["utilisateur"] for p in collection_paniers.find()] if collection_paniers else []
            if not paniers_list:
                st.info("Aucun panier à supprimer")
            else:
                panier_user = st.selectbox("Sélectionner un panier", paniers_list, key="panier_sup_select")
                
                if st.form_submit_button("🗑️ Supprimer"):
                    if not check_connection():
                        st.error("Opération impossible en mode déconnecté")
                    else:
                        result = collection_paniers.delete_one({"utilisateur": panier_user})
                        if result.deleted_count:
                            st.success("Panier supprimé avec succès ✅")
                        else:
                            st.error("Erreur lors de la suppression")

# ======================
# ==== COMMANDES =======
# ======================
with tabs[3]:
    create_section("Gestion des commandes")
    commandes_tab = st.tabs(["📋 Afficher", "➕ Créer", "🗑️ Supprimer"])

    # 1. Affichage des commandes
    with commandes_tab[0]:
        if check_connection():
            commandes = list(collection_commandes.find()) if collection_commandes else []
            if commandes:
                st.success(f"📋 {len(commandes)} commandes trouvées")
                for c in commandes:
                    with st.expander(f"📦 Commande du {c['date']} - {c['utilisateur']}"):
                        st.json(c)
            else:
                st.info("Aucune commande enregistrée.")

    # 2. Création de commande
    with commandes_tab[1]:
        with st.form("creer_commande"):
            utilisateurs = [u["email"] for u in collection_users.find()] if collection_users else []
            if not utilisateurs:
                st.warning("Aucun utilisateur trouvé.")
            else:
                utilisateur = st.selectbox("Utilisateur*", utilisateurs, key="commande_creer_utilisateur")
                produits = [p["nom"] for p in collection.find()] if collection else []
                
                st.markdown("**📦 Produits commandés :**")
                produits_choisis = st.multiselect(
                    "Sélectionner les produits", 
                    produits, 
                    key="commande_creer_produits"
                )
                
                quantites = {}
                cols = st.columns(2)
                for i, p in enumerate(produits_choisis):
                    with cols[i % 2]:
                        qte = st.number_input(
                            f"Quantité pour {p}",
                            1, 
                            key=f"commande_creer_qte_{p}",
                            help=f"Stock disponible: {collection.find_one({'nom': p})['stock'] if collection and collection.find_one({'nom': p}) else 0}"
                        )
                        quantites[p] = qte
                
                cols = st.columns(2)
                with cols[0]:
                    paiement = st.selectbox("Statut paiement*", ["non payé", "payé"], key="commande_creer_paiement")
                with cols[1]:
                    livraison = st.selectbox("Statut livraison*", ["en attente", "livré"], key="commande_creer_livraison")
                
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if st.form_submit_button("📦 Enregistrer commande"):
                    if not check_connection():
                        st.error("Opération impossible en mode déconnecté")
                    else:
                        if utilisateur and quantites:
                            # Calcul du total de la commande
                            total = sum(collection.find_one({"nom": p})["prix"] * q for p, q in quantites.items())
                            cmd = {
                                "utilisateur": utilisateur,
                                "produits": quantites,
                                "date": date,
                                "paiement": paiement,
                                "livraison": livraison,
                                "total": total,
                                "statut": "en cours"
                            }
                            # Insertion de la commande
                            commande_id = collection_commandes.insert_one(cmd).inserted_id
                            # Mise à jour de l'historique de l'utilisateur
                            collection_users.update_one(
                                {"email": utilisateur},
                                {"$push": {"historique_achats": commande_id}}
                            )
                            
                            # Mise à jour du stock des produits
                            for p, q in quantites.items():
                                collection.update_one({"nom": p}, {"$inc": {"stock": -q}})
                            
                            st.success(f"Commande enregistrée avec succès ✅ Total: {total:.2f} DH")
                        else:
                            st.warning("Veuillez sélectionner au moins un produit")

    # 3. Suppression de commande
    with commandes_tab[2]:
        with st.form("supprimer_commande"):
            commandes_list = [c["_id"] for c in collection_commandes.find()] if collection_commandes else []
            if not commandes_list:
                st.info("Aucune commande à supprimer")
            else:
                commande_id = st.selectbox(
                    "Sélectionner une commande",
                    commandes_list,
                    format_func=lambda x: str(x),
                    key="commande_sup_select"
                )
                
                if st.form_submit_button("🗑️ Supprimer"):
                    if not check_connection():
                        st.error("Opération impossible en mode déconnecté")
                    else:
                        # Trouver l'utilisateur associé pour mettre à jour son historique
                        commande = collection_commandes.find_one({"_id": commande_id})
                        if commande:
                            collection_users.update_one(
                                {"email": commande["utilisateur"]},
                                {"$pull": {"historique_achats": commande_id}}
                            )
                        
                        result = collection_commandes.delete_one({"_id": commande_id})
                        if result.deleted_count:
                            st.success("Commande supprimée avec succès ✅")
                        else:
                            st.error("Erreur lors de la suppression")

# ===================
# ==== AVIS =========
# ===================
with tabs[4]:
    create_section("Gestion des avis")
    avis_tab = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])

    # 1. Affichage des avis
    with avis_tab[0]:
        if check_connection():
            avis = list(collection_avis.find()) if collection_avis else []
            if avis:
                st.success(f"⭐ {len(avis)} avis trouvés")
                for a in avis:
                    with st.expander(f"🌟 {a['note']}/5 - {a['produit']} par {a['utilisateur']}"):
                        st.json(a)
            else:
                st.info("Aucun avis trouvé.")

    # 2. Ajout d'avis
    with avis_tab[1]:
        with st.form("ajouter_avis"):
            produits = [p["nom"] for p in collection.find()] if collection else []
            utilisateurs = [u["email"] for u in collection_users.find()] if collection_users else []
            
            cols = st.columns(2)
            with cols[0]:
                produit = st.selectbox("Produit*", produits, key="avis_aj_prod")
            with cols[1]:
                utilisateur = st.selectbox("Utilisateur*", utilisateurs, key="avis_aj_user")
            
            commentaire = st.text_area("Commentaire*", key="avis_aj_commentaire", height=100)
            note = st.slider("Note*", 0, 5, 3, key="avis_aj_note")
            
            if st.form_submit_button("⭐ Ajouter avis"):
                if not check_connection():
                    st.error("Opération impossible en mode déconnecté")
                else:
                    if produit and utilisateur and commentaire:
                        avis_doc = {
                            "produit": produit,
                            "utilisateur": utilisateur,
                            "commentaire": commentaire,
                            "note": note,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "valide": True
                        }
                        collection_avis.insert_one(avis_doc)
                        # Mise à jour de la popularité du produit
                        collection.update_one({"nom": produit}, {"$inc": {"popularite": 1}})
                        st.success("Avis ajouté avec succès ✅")
                    else:
                        st.warning("Tous les champs marqués d'un * sont obligatoires")

    # 3. Suppression d'avis
    with avis_tab[2]:
        with st.form("supprimer_avis"):
            avis_list = list(collection_avis.find()) if collection_avis else []
            if not avis_list:
                st.info("Aucun avis à supprimer")
            else:
                avis_options = [
                    (str(a["_id"]), f"{a['note']}/5 - {a['produit']} par {a['utilisateur']}")
                    for a in avis_list
                ]
                avis_selected = st.selectbox(
                    "Sélectionner un avis à supprimer",
                    [a[0] for a in avis_options],
                    format_func=lambda x: next(a[1] for a in avis_options if a[0] == x),
                    key="avis_sup_select"
                )
                
                if st.form_submit_button("🗑️ Supprimer"):
                    if not check_connection():
                        st.error("Opération impossible en mode déconnecté")
                    else:
                        try:
                            # Décrémenter la popularité du produit associé
                            avis = collection_avis.find_one({"_id": ObjectId(avis_selected)})
                            if avis:
                                collection.update_one(
                                    {"nom": avis["produit"]}, 
                                    {"$inc": {"popularite": -1}}
                                )
                            
                            result = collection_avis.delete_one({"_id": ObjectId(avis_selected)})
                            if result.deleted_count:
                                st.success("Avis supprimé avec succès ✅")
                            else:
                                st.warning("Avis non trouvé")
                        except Exception as e:
                            st.error(f"Erreur : {str(e)}")

# Pied de page
st.markdown("""
<div style="margin-top: 50px; padding: 20px; background: linear-gradient(135deg, #4361ee, #3f37c9); color: white; border-radius: 10px;">
    <table style="width: 100%;">
        <tr>
            <td style="text-align: left; width: 49%;">
                <p><strong>Encadré par :</strong><br>
                Pr S.CHERDAL<br>
                Mme Noussaiba Daali</p>
            </td>
            <td style="width: 1px; background-color: white; border-radius: 10px;
                       box-shadow: 0 0 8px rgba(255,255,255,0.5);"></td>
            <td style="text-align: left; width: 49%;">
                <p><strong>Réalisé par :</strong><br>
                EL MOUTAOUAKIL Khalid<br>
                HAMOUDAN Badreddine</p>
            </td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)
