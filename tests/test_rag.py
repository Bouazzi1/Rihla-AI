"""
Script de test simple pour vérifier que RihlaRetriever
trouve bien les bonnes informations dans ChromaDB.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.retriever import RihlaRetriever

def main():
    print("🤖 Initialisation RihlaRetriever...")
    retriever = RihlaRetriever()
    
    queries = [
        ("Quels sont les jours d'ouverture ?", "faq"),
        ("Je cherche une omra de 15 jours", "omra"),
        ("Comment annuler mon voyage ?", "administratif"),
        ("Faut-il un visa pour la Turquie ?", "visa")
    ]
    
    for q, intent in queries:
        print(f"\n❓ Question: '{q}' (Intent: {intent})")
        context = retriever.get_context_for_prompt(q, intent=intent)
        print("💡 Contexte récupéré :")
        print(context)

if __name__ == "__main__":
    main()
