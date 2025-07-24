import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# 🔧 Configuration : Choisissez la bonne URI
MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"

# 📦 Nom de la base de données à utiliser
DB_NAME = "transport_db"

def connect_to_mongodb():
    try:
        print(f"🟡 Tentative de connexion à MongoDB...\nURI: {MONGO_URI}")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

        # 🧪 Forcer la détection de l’état du cluster
        client.admin.command('ping')

        db = client[DB_NAME]
        print("✅ Connexion réussie à MongoDB.")
        return db

    except errors.ServerSelectionTimeoutError as err:
        print("🚫 Échec de la connexion : MongoDB injoignable.")
        print("🧩 Détails de l’erreur :", err)

        if "Connection refused" in str(err):
            print("📌 Vérifiez si MongoDB est démarré (localhost) ou si le cluster Atlas est actif.")
            print("💡 Conseil :")
            print(" - Si vous utilisez localhost, lancez MongoDB avec `mongod`.")
            print(" - Si vous utilisez Atlas, vérifiez :")
            print("     ▪️ Le cluster est actif.")
            print("     ▪️ Votre IP est bien ajoutée dans Network Access.")
            print("     ▪️ L’utilisateur a les bons identifiants.")
        elif "Authentication failed" in str(err):
            print("🔑 Erreur d’authentification : Vérifiez l'utilisateur/mot de passe.")
        else:
            print("🛑 Une erreur inattendue est survenue.")

        return None

# Test de connexion
if __name__ == "__main__":
    db = connect_to_mongodb()
    if db:
        print("🎯 Accès à la base de données :", db.name)
    else:
        print("❌ Impossible d'accéder à la base MongoDB.")
