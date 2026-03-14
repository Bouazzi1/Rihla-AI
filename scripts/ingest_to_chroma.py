"""
Rihla-AI — Scripts d'ingestion vers ChromaDB (Phase 2)
Lit les fichiers JSON de la Knowledge Base et les insère dans ChromaDB.
"""

import sys
import json
from pathlib import Path

import chromadb

# Config paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

CHROMA_PATH = settings.CHROMA_PATH
DATA_DIR = Path(__file__).parent.parent / "data"

def init_chroma():
    """Initialise le client ChromaDB local."""
    print(f"🔌 Connexion à ChromaDB dans {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client

def ingest_faq(client):
    """Ingère la FAQ."""
    collection = client.get_or_create_collection(
        name="faq",
        metadata={"description": "Foire aux questions Rihla-AI"}
    )
    
    with open(DATA_DIR / "knowledge_base" / "faq.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for i, item in enumerate(data.get("faq", [])):
        q = item["q"]
        a = item["a"]
        # Le document indexé est la question pour matcher l'intention de l'utilisateur
        # On stocke la réponse en metadata
        collection.upsert(
            documents=[q],
            metadatas=[{"reponse": a, "type": "faq"}],
            ids=[f"faq_{i}"]
        )
    print(f"✅ FAQ ingérée ({len(data.get('faq', []))} entrées)")


def ingest_visa(client):
    """Ingère les règles de visa."""
    collection = client.get_or_create_collection(
        name="visa",
        metadata={"description": "Conditions de visa par pays"}
    )
    
    with open(DATA_DIR / "knowledge_base" / "visa_rules.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for i, item in enumerate(data.get("visa", [])):
        pays = item["pays"]
        exigences = item["exigences"]
        
        collection.upsert(
            documents=[f"visa {pays} conditions"],
            metadatas=[{"pays": pays, "exigences": exigences, "type": "visa"}],
            ids=[f"visa_{i}"]
        )
    print(f"✅ Règles Visa ingérées ({len(data.get('visa', []))} pays)")


def ingest_procedures(client):
    """Ingère les procédures de l'agence."""
    collection = client.get_or_create_collection(
        name="procedures",
        metadata={"description": "Procédures de réservation et annulation"}
    )
    
    with open(DATA_DIR / "knowledge_base" / "procedures.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for i, item in enumerate(data.get("procedures", [])):
        titre = item["titre"]
        etapes = "\n".join([f"- {e}" for e in item["etapes"]])
        
        # On indexe le titre complet avec le mot procédure
        collection.upsert(
            documents=[f"procédure {titre}"],
            metadatas=[{"titre": titre, "etapes": etapes, "type": "procedure"}],
            ids=[f"proc_{i}"]
        )
    print(f"✅ Procédures ingérées ({len(data.get('procedures', []))} entrées)")


def ingest_programmes(client):
    """Ingère les programmes Omra et Tourisme."""
    collection = client.get_or_create_collection(
        name="programmes",
        metadata={"description": "Voyages Omra et Tourisme disponibles"}
    )
    
    # Omra
    try:
        with open(DATA_DIR / "programmes" / "omra_packages.json", "r", encoding="utf-8") as f:
            omra_data = json.load(f)
        for p in omra_data.get("programmes", []):
            desc = f"Omra {p['nom']} {p['prix_base_tnd']} TND"
            collection.upsert(
                documents=[desc],
                metadatas=[{
                    "id": p["id"], "nom": p["nom"], "type": "omra",
                    "prix": p["prix_base_tnd"], "inclus": ", ".join(p["inclus"])
                }],
                ids=[p["id"]]
            )
        print(f"✅ Programmes Omra ingérés ({len(omra_data.get('programmes', []))} packages)")
    except FileNotFoundError:
         print("❌ Fichier omra_packages.json introuvable.")
    
    # Tourisme
    try:
        with open(DATA_DIR / "programmes" / "tourism_packages.json", "r", encoding="utf-8") as f:
            tour_data = json.load(f)
        for p in tour_data.get("programmes", []):
            destinations = " ".join(p["destinations"])
            desc = f"Voyage tourisme {p['nom']} {destinations} {p['prix_base_tnd']} TND"
            collection.upsert(
                documents=[desc],
                metadatas=[{
                    "id": p["id"], "nom": p["nom"], "type": "tourisme",
                    "prix": p["prix_base_tnd"], "destinations": destinations
                }],
                ids=[p["id"]]
            )
        print(f"✅ Programmes Tourisme ingérés ({len(tour_data.get('programmes', []))} packages)")
    except FileNotFoundError:
        print("❌ Fichier tourism_packages.json introuvable.")


if __name__ == "__main__":
    print("🚀 Début de l'ingestion vers ChromaDB...")
    client = init_chroma()
    ingest_faq(client)
    ingest_visa(client)
    ingest_procedures(client)
    ingest_programmes(client)
    print("🎉 Ingestion terminée avec succès !")
