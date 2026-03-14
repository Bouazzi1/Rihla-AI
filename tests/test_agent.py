"""
Rihla-AI — Agent Integration Test (Phase 3)
Verifie que le StateGraph LangGraph fonctionne correctement de bout en bout
(sans passer par le serveur FastAPI).
"""

import sys
import asyncio
from pathlib import Path

# Config paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.graph import agent

async def main():
    print("🤖=== Lancement du test LangGraph ===")
    
    test_queries = [
        "Bonjour, avez-vous des offres pour une Omra de 10 jours ?",
        "Quels sont vos horaires complets d'ouverture svp ?",
        "Je voudrais savoir s'il faut un visa pour aller en Espagne cet été.",
    ]
    
    for query in test_queries:
        print(f"\n👤 USER: {query}")
        
        reply, intent, context = await agent.process_message(user_message=query)
        
        print(f"🎯 INTENT DÉTECTÉ : {intent}")
        print(f"🔗 CONTEXTE UTILISÉ : {context[:100]}...")
        print(f"🤖 AGENT : {reply}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
