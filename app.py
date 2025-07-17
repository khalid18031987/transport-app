import streamlit as st
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from PIL import Image
import numpy as np

# Configuration MongoDB avec les secrets Streamlit
uri = st.secrets["MONGODB_URI"]
db_name = st.secrets["MONGO_DB"]

# Connexion MongoDB
client = MongoClient(uri)
db = client[db_name]

# Accès aux collections avec fallback sur les noms par défaut
produits = db[st.secrets.get("MONGO_COLLECTION", "produits")]
utilisateurs = db[st.secrets.get("MONGO_COLLECTION_UTILISATEURS", "utilisateurs")]
paniers = db[st.secrets.get("MONGO_COLLECTION_PANIERS", "paniers")]
commandes = db[st.secrets.get("MONGO_COLLECTION_COMMANDES", "commandes")]
avis = db[st.secrets.get("MONGO_COLLECTION_AVIS", "avis")]

# Config Streamlit
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
    </style>
""", unsafe_allow_html=True)

# En-tête avec image
try:
    image = Image.open("transport.jpeg")
    image_array = np.array(image)
    st.image(image_array, use_container_width=True, 
             caption="Système de Gestion de Transport", 
             output_format="JPEG")
except FileNotFoundError:
    st.error("L'image transport.jpeg est introuvable. Veuillez placer l'image dans le même répertoire que ce script.")
    st.image("https://via.placeholder.com/1200x300?text=Transport+System", use_container_width=True)

# Catégories de produits
categories = [
    "Ticket simple", "Abonnement mensuel", "Carte rechargeable", "Carte étudiant",
    "Réservation VIP", "Assistance bagage", "QR Code voyage", "Recharge carte",
    "Crédits de trajet", "Abonnement élève", "Badge bus scolaire",
    "Carte entreprise", "Badge chauffeur", "autre"
]

# Fonction pour créer une section
def create_section(title):
    st.markdown(f'<div class="section"><div class="section-title">{title}</div>', unsafe_allow_html=True)

# --- Onglets principaux ---
tab_titles = ["📦 Produits", "👥 Utilisateurs", "🛒 Paniers", "📋 Commandes", "⭐ Avis"]
tabs = st.tabs(tab_titles)

# ====================
# ==== PRODUITS ======
# ====================
with tabs[0]:
    create_section("Gestion des produits")
    prod_tab = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer", "🔍 Filtrer"])

    # Afficher
    with prod_tab[0]:
        # Barre de recherche
        search_term = st.text_input("🔍 Rechercher un produit par nom")
        
        query = {}
        if search_term:
            query["nom"] = {"$regex": search_term, "$options": "i"}
            
        produits_list = list(produits.find(query))
        if produits_list:
            st.success(f"📊 {len(produits_list)} produits trouvés")
            for p in produits_list:
                with st.expander(f"🔹 {p.get('nom', 'Sans nom')} - {p.get('prix', 0)}€ (Stock: {p.get('stock', 0)})"):
                    st.markdown(f"""
                    **🆔 ID**: `{p.get('_id')}`  
                    **📦 Nom**: {p.get('nom', 'Non spécifié')}  
                    **💰 Prix**: {p.get('prix', 'Non défini')} MAD  
                    **📂 Catégorie**: {p.get('categorie', 'Non définie')}  
                    **📝 Description**: {p.get('description', 'Aucune description')}  
                    **📅 Date création**: {p.get('date_creation', 'Inconnue')}  
                    **⭐ Popularité**: {p.get('popularite', 0)}  
                    """)
        else:
            st.info("Aucun produit trouvé.")

    # Ajouter
    with prod_tab[1]:
        with st.form("ajouter_produit"):
            cols = st.columns(2)
            with cols[0]:
                nom = st.text_input("Nom du produit*", key="prod_aj_nom")
                description = st.text_area("Description*", key="prod_aj_desc")
            with cols[1]:
                prix = st.number_input("Prix*", 0.0, key="prod_aj_prix", step=0.5)
                stock = st.number_input("Stock*", 0, key="prod_aj_stock")
                categorie = st.selectbox("Catégorie*", categories, key="prod_aj_cat")
            
            if st.form_submit_button("➕ Ajouter produit"):
                if nom and description and categorie:
                    produits.insert_one({
                        "nom": nom,
                        "description": description,
                        "prix": prix,
                        "stock": stock,
                        "categorie": categorie,
                        "popularite": 0,
                        "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("Produit ajouté avec succès ✅")
                    st.experimental_rerun()
                else:
                    st.warning("Veuillez remplir tous les champs obligatoires (*)")

    # Supprimer
    with prod_tab[2]:
        with st.form("supprimer_produit"):
            produits_liste = [p["nom"] for p in produits.find()]
            produit = st.selectbox("Sélectionner un produit à supprimer", produits_liste, key="prod_sup_select")
            
            if st.form_submit_button("🗑️ Supprimer"):
                result = produits.delete_one({"nom": produit})
                if result.deleted_count:
                    st.success("Produit supprimé avec succès ✅")
                    st.experimental_rerun()
                else:
                    st.error("Erreur lors de la suppression")

    # Filtrer
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
                query = {}
                if categorie != "Toutes":
                    query["categorie"] = categorie
                query["prix"] = {"$gte": prix_min, "$lte": prix_max}
                query["popularite"] = {"$gte": pop_min}
                query["stock"] = {"$gte": stock_min}
                
                produits_filtres = list(produits.find(query))
                if produits_filtres:
                    st.success(f"🔎 {len(produits_filtres)} produits correspondent aux critères")
                    for p in produits_filtres:
                        with st.expander(f"{p.get('nom', 'Sans nom')} - {p.get('prix', 0)}€"):
                            st.markdown(f"""
                            **📦 Nom**: {p.get('nom', 'Non spécifié')}  
                            **💰 Prix**: {p.get('prix', 'Non défini')} MAD  
                            **📂 Catégorie**: {p.get('categorie', 'Non définie')}  
                            **📝 Description**: {p.get('description', 'Aucune description')}  
                            **📅 Date création**: {p.get('date_creation', 'Inconnue')}  
                            **⭐ Popularité**: {p.get('popularite', 0)}  
                            **📊 Stock**: {p.get('stock', 0)}  
                            """)
                else:
                    st.warning("Aucun produit ne correspond aux critères.")

# =========================
# ==== UTILISATEURS =======
# =========================
with tabs[1]:
    create_section("Gestion des utilisateurs")
    user_tab = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])

    with user_tab[0]:
        users = list(utilisateurs.find())
        if users:
            st.success(f"👥 {len(users)} utilisateurs trouvés")
            for u in users:
                with st.expander(f"""👤 {u.get('nom', 'Sans nom')} - {u.get('email', "Pas d'email")}"""):
                    st.markdown(f"""
                    **📧 Email**: {u.get('email', 'Non spécifié')}  
                    **🏠 Adresse**: {u.get('adresse', 'Non spécifiée')}  
                    **📞 Téléphone**: {u.get('telephone', 'Non spécifié')}  
                    **📅 Date inscription**: {u.get('date_inscription', 'Inconnue')}  
                    """)
                    
                    historique = u.get("historique_achats", [])
                    if historique:
                        st.markdown("**📜 Historique d'achats :**")
                        for com_id in historique:
                            com = commandes.find_one({"_id": com_id}) if commandes else None
                            if com:
                                st.json(com)
                    else:
                        st.info("Aucun historique d'achats")
        else:
            st.info("Aucun utilisateur trouvé.")

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
                if nom and email and adresse:
                    if utilisateurs.find_one({"email": email}):
                        st.error("Cet email est déjà utilisé")
                    else:
                        utilisateurs.insert_one({
                            "nom": nom,
                            "email": email,
                            "adresse": adresse,
                            "telephone": telephone,
                            "date_inscription": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "historique_achats": []
                        })
                        st.success("Utilisateur ajouté avec succès ✅")
                        st.experimental_rerun()
                else:
                    st.warning("Veuillez remplir les champs obligatoires (*)")

    with user_tab[2]:
        with st.form("supprimer_utilisateur"):
            users_list = [u["email"] for u in utilisateurs.find()]
            user_email = st.selectbox("Sélectionner un utilisateur", users_list, key="user_sup_select")
            
            if st.form_submit_button("🗑️ Supprimer"):
                result = utilisateurs.delete_one({"email": user_email})
                if result.deleted_count:
                    st.success("Utilisateur supprimé avec succès ✅")
                    st.experimental_rerun()
                else:
                    st.error("Erreur lors de la suppression")

# =====================
# ==== PANIERS ========
# =====================
with tabs[2]:
    create_section("Gestion des paniers")
    panier_tab = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])

    with panier_tab[0]:
        paniers_list = list(paniers.find())
        if paniers_list:
            st.success(f"🛒 {len(paniers_list)} paniers trouvés")
            for p in paniers_list:
                with st.expander(f"🛍️ Panier de {p.get('utilisateur', 'Inconnu')} - Total: {p.get('total', 0)}€"):
                    st.json(p)
        else:
            st.info("Aucun panier trouvé.")

    with panier_tab[1]:
        with st.form("ajouter_panier"):
            users = [u["email"] for u in utilisateurs.find()]
            if not users:
                st.warning("Aucun utilisateur disponible.")
            else:
                utilisateur = st.selectbox("Utilisateur*", users, key="panier_aj_utilisateur")
                produits_list = [p["nom"] for p in produits.find()]
                
                st.markdown("**📦 Sélection des produits :**")
                cols = st.columns(2)
                quantites = {}
                for i, produit in enumerate(produits_list):
                    with cols[i % 2]:
                        qte = st.number_input(
                            f"Quantité pour {produit}",
                            0, 
                            key=f"panier_aj_qte_{produit}",
                            help=f"Stock disponible: {produits.find_one({'nom': produit})['stock']}"
                        )
                        if qte > 0:
                            quantites[produit] = qte
                
                if st.form_submit_button("➕ Ajouter panier"):
                    if utilisateur and quantites:
                        total = sum(produits.find_one({"nom": p})["prix"] * q for p, q in quantites.items())
                        paniers.insert_one({
                            "utilisateur": utilisateur,
                            "produits": quantites,
                            "total": total,
                            "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.success(f"Panier ajouté avec succès ✅ Total: {total:.2f} €")
                        st.experimental_rerun()
                    else:
                        st.warning("Veuillez sélectionner au moins un produit")

    with panier_tab[2]:
        with st.form("supprimer_panier"):
            paniers_list = [p["utilisateur"] for p in paniers.find()]
            if not paniers_list:
                st.info("Aucun panier à supprimer")
            else:
                panier_user = st.selectbox("Sélectionner un panier", paniers_list, key="panier_sup_select")
                
                if st.form_submit_button("🗑️ Supprimer"):
                    result = paniers.delete_one({"utilisateur": panier_user})
                    if result.deleted_count:
                        st.success("Panier supprimé avec succès ✅")
                        st.experimental_rerun()
                    else:
                        st.error("Erreur lors de la suppression")

# ======================
# ==== COMMANDES =======
# ======================
with tabs[3]:
    create_section("Gestion des commandes")
    commandes_tab = st.tabs(["📋 Afficher", "➕ Créer", "🗑️ Supprimer"])

    with commandes_tab[0]:
        commandes_list = list(commandes.find())
        if commandes_list:
            st.success(f"📋 {len(commandes_list)} commandes trouvées")
            for c in commandes_list:
                with st.expander(f"📦 Commande du {c.get('date', 'Date inconnue')} - {c.get('utilisateur', 'Utilisateur inconnu')}"):
                    st.json(c)
        else:
            st.info("Aucune commande enregistrée.")

    with commandes_tab[1]:
        with st.form("creer_commande"):
            users = [u["email"] for u in utilisateurs.find()]
            if not users:
                st.warning("Aucun utilisateur trouvé.")
            else:
                utilisateur = st.selectbox("Utilisateur*", users, key="commande_creer_utilisateur")
                produits_list = [p["nom"] for p in produits.find()]
                
                st.markdown("**📦 Produits commandés :**")
                produits_choisis = st.multiselect(
                    "Sélectionner les produits", 
                    produits_list, 
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
                            help=f"Stock disponible: {produits.find_one({'nom': p})['stock']}"
                        )
                        quantites[p] = qte
                
                cols = st.columns(2)
                with cols[0]:
                    paiement = st.selectbox("Statut paiement*", ["non payé", "payé"], key="commande_creer_paiement")
                with cols[1]:
                    livraison = st.selectbox("Statut livraison*", ["en attente", "livré"], key="commande_creer_livraison")
                
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if st.form_submit_button("📦 Enregistrer commande"):
                    if utilisateur and quantites:
                        total = sum(produits.find_one({"nom": p})["prix"] * q for p, q in quantites.items())
                        cmd = {
                            "utilisateur": utilisateur,
                            "produits": quantites,
                            "date": date,
                            "paiement": paiement,
                            "livraison": livraison,
                            "total": total,
                            "statut": "en cours"
                        }
                        commande_id = commandes.insert_one(cmd).inserted_id
                        
                        utilisateurs.update_one(
                            {"email": utilisateur},
                            {"$push": {"historique_achats": commande_id}}
                        )
                        
                        # Mise à jour du stock
                        for p, q in quantites.items():
                            produits.update_one({"nom": p}, {"$inc": {"stock": -q}})
                        
                        st.success(f"Commande enregistrée avec succès ✅ Total: {total:.2f} €")
                        st.experimental_rerun()
                    else:
                        st.warning("Veuillez sélectionner au moins un produit")

    with commandes_tab[2]:
        with st.form("supprimer_commande"):
            commandes_list = [c["_id"] for c in commandes.find()]
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
                    # Trouver l'utilisateur associé pour mettre à jour son historique
                    commande = commandes.find_one({"_id": commande_id})
                    if commande:
                        utilisateurs.update_one(
                            {"email": commande["utilisateur"]},
                            {"$pull": {"historique_achats": commande_id}}
                        )
                    
                    result = commandes.delete_one({"_id": commande_id})
                    if result.deleted_count:
                        st.success("Commande supprimée avec succès ✅")
                        st.experimental_rerun()
                    else:
                        st.error("Erreur lors de la suppression")

# ===================
# ==== AVIS =========
# ===================
with tabs[4]:
    create_section("Gestion des avis")
    avis_tab = st.tabs(["📋 Afficher", "➕ Ajouter", "🗑️ Supprimer"])

    with avis_tab[0]:
        avis_list = list(avis.find())
        if avis_list:
            st.success(f"⭐ {len(avis_list)} avis trouvés")
            for a in avis_list:
                with st.expander(f"🌟 {a.get('note', 0)}/5 - {a.get('produit', 'Produit inconnu')} par {a.get('utilisateur', 'Utilisateur inconnu')}"):
                    st.json(a)
        else:
            st.info("Aucun avis trouvé.")

    with avis_tab[1]:
        with st.form("ajouter_avis"):
            produits_list = [p["nom"] for p in produits.find()]
            users = [u["email"] for u in utilisateurs.find()]
            
            cols = st.columns(2)
            with cols[0]:
                produit = st.selectbox("Produit*", produits_list, key="avis_aj_prod")
            with cols[1]:
                utilisateur = st.selectbox("Utilisateur*", users, key="avis_aj_user")
            
            commentaire = st.text_area("Commentaire*", key="avis_aj_commentaire", height=100)
            note = st.slider("Note*", 0, 5, 3, key="avis_aj_note")
            
            if st.form_submit_button("⭐ Ajouter avis"):
                if produit and utilisateur and commentaire:
                    avis_doc = {
                        "produit": produit,
                        "utilisateur": utilisateur,
                        "commentaire": commentaire,
                        "note": note,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "valide": True
                    }
                    avis.insert_one(avis_doc)
                    produits.update_one({"nom": produit}, {"$inc": {"popularite": 1}})
                    st.success("Avis ajouté avec succès ✅")
                    st.experimental_rerun()
                else:
                    st.warning("Tous les champs marqués d'un * sont obligatoires")

    with avis_tab[2]:
        with st.form("supprimer_avis"):
            avis_list = list(avis.find())
            if not avis_list:
                st.info("Aucun avis à supprimer")
            else:
                avis_options = [
                    (str(a["_id"]), f"{a.get('note', 0)}/5 - {a.get('produit', 'Produit inconnu')} par {a.get('utilisateur', 'Utilisateur inconnu')}")
                    for a in avis_list
                ]
                avis_selected = st.selectbox(
                    "Sélectionner un avis à supprimer",
                    [a[0] for a in avis_options],
                    format_func=lambda x: next(a[1] for a in avis_options if a[0] == x),
                    key="avis_sup_select"
                )
                
                if st.form_submit_button("🗑️ Supprimer"):
                    try:
                        # Décrémenter la popularité du produit
                        avis_doc = avis.find_one({"_id": ObjectId(avis_selected)})
                        if avis_doc:
                            produits.update_one(
                                {"nom": avis_doc["produit"]}, 
                                {"$inc": {"popularite": -1}}
                            )
                        
                        result = avis.delete_one({"_id": ObjectId(avis_selected)})
                        if result.deleted_count:
                            st.success("Avis supprimé avec succès ✅")
                            st.experimental_rerun()
                        else:
                            st.warning("Avis non trouvé")
                    except Exception as e:
                        st.error(f"Erreur : {str(e)}")

# Pied de page
st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 20px; background: linear-gradient(135deg, #4361ee, #3f37c9); color: white; border-radius: 10px;">
        <p>Système de Gestion de Transport - © 2023 Tous droits réservés</p>
    </div>
""", unsafe_allow_html=True)
