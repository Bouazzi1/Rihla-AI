"""
Rihla-AI — RAG Retriever (Phase 2)
Fonctions pour interroger ChromaDB et récupérer le contexte pertinent
pour l'agent conversationnel.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

import chromadb

# Config paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

class RihlaRetriever:
    """Gestionnaire de recherche sémantique dans la Knowledge Base ChromaDB."""
    
    def __init__(self):
        self.chroma_path = settings.CHROMA_PATH
        self.client = chromadb.PersistentClient(path=str(self.chroma_path))
        
        # Récupérer les collections existantes
        self.collections = {
            "faq": self.client.get_or_create_collection("faq"),
            "visa": self.client.get_or_create_collection("visa"),
            "procedures": self.client.get_or_create_collection("procedures"),
            "programmes": self.client.get_or_create_collection("programmes"),
        }
        
    def search(self, query: str, collection_name: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """
        Effectue une recherche sémantique sur une collection spécifique.
        
        Args:
            query (str): La requête de l'utilisateur (ex: "Quel est le prix de la omra VIP ?")
            collection_name (str): Nom de la collection ("faq", "visa", "procedures", "programmes")
            n_results (int): Nombre de résultats à retourner
            
        Returns:
            List[Dict]: Les documents trouvés avec leurs métadonnées
        """
        if collection_name not in self.collections:
            return []
            
        collection = self.collections[collection_name]
        
        # On interroge ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Formater la réponse
        formatted_results = []
        
        if results and results['metadatas'] and len(results['metadatas']) > 0:
            # results['metadatas'] est une liste (pour chaque query) de listes (pour chaque résultat)
            metadatas = results['metadatas'][0]
            documents = results['documents'][0] if 'documents' in results else []
            distances = results['distances'][0] if 'distances' in results else []
            
            for i in range(len(metadatas)):
                formatted_results.append({
                    "content": documents[i] if i < len(documents) else "",
                    "metadata": metadatas[i],
                    "score": distances[i] if i < len(distances) else None
                })
                
        return formatted_results

    def search_all(self, query: str, n_results_per_collection: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recherche dans toutes les collections en même temps.
        Utile quand l'intention de l'utilisateur n'est pas encore classifiée avec certitude.
        """
        all_results = {}
        for name in self.collections.keys():
            results = self.search(query, name, n_results=n_results_per_collection)
            if results:
                all_results[name] = results
        return all_results

    def get_context_for_prompt(self, query: str, intent: str = None) -> str:
        """
        Construit le bloc de contexte texte à injecter dans le prompt du LLM.
        Si l'intent est connu (ex: "devis"), on priorise la collection correspondante.
        """
        context_parts = []
        
        # Si c'est une intention de devis/voyage, on cherche dans les programmes en priorité
        if intent in ["devis", "reservation", "voyage", "omra"]:
            progs = self.search(query, "programmes", n_results=2)
            for p in progs:
                m = p["metadata"]
                context_parts.append(f"[Programme {m.get('id')}] {m.get('nom')} - Prix: {m.get('prix')} TND - Inclut: {m.get('inclus', m.get('destinations'))}")
                
        # Si c'est une question administrative
        elif intent in ["visa", "administratif"]:
            visas = self.search(query, "visa", n_results=1)
            for v in visas:
                m = v["metadata"]
                context_parts.append(f"[Visa {m.get('pays')}] Exigences: {m.get('exigences')}")
                
            procs = self.search(query, "procedures", n_results=1)
            for p in procs:
                m = p["metadata"]
                context_parts.append(f"[Procédure {m.get('titre')}] Étapes: {m.get('etapes')}")
                
        # Par défaut, on cherche dans la FAQ et on pioche partout
        if not context_parts:
            faqs = self.search(query, "faq", n_results=2)
            for f in faqs:
                m = f["metadata"]
                context_parts.append(f"[FAQ] Question: {f['content']} -> Réponse: {m.get('reponse')}")
                
            # Fallback global si vraiment rien n'est trouvé
            if not context_parts:
                all_res = self.search_all(query, n_results_per_collection=1)
                for coll_name, items in all_res.items():
                    for item in items:
                        context_parts.append(f"[{coll_name.upper()}] {item['content']} - {item['metadata']}")

        if not context_parts:
            return "Aucune information de la base de connaissances n'est pertinente pour cette requête."
            
        return "CONTEXTE AGENCE RIHLA :\n" + "\n".join(context_parts)
