"""
Rihla-AI — Agent Nodes (Phase 3)
Les différents noeuds du graphe LangGraph.
"""

import sys
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_models import ChatOllama

# Config paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import settings
from src.agents.state import AgentState
from src.agents.prompts import INTENT_SYSTEM_PROMPT, GENERATION_SYSTEM_PROMPT
from src.rag.retriever import RihlaRetriever

# Initialisation LLM et RAG
llm = ChatOllama(
    model="llama3.2:3b",
    base_url=settings.OLLAMA_HOST,
    temperature=0.1 # Basse température pour la précision
)
retriever = RihlaRetriever()

def classify_intent_node(state: AgentState):
    """
    Détermine l'intention du dernier message utilisateur.
    """
    print("🧠 Node: classify_intent")
    # Récupérer le dernier message utilisateur
    latest_msg = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    
    if not latest_msg:
         return {"intent": "other"}

    prompt = INTENT_SYSTEM_PROMPT.format(user_message=latest_msg)
    
    # Appel LLM avec temp très basse (0.0)
    llm_classifier = ChatOllama(model="llama3.2:3b", base_url=settings.OLLAMA_HOST, temperature=0.0)
    # Llama 3 réagit mieux quand les instructions système sont traitées et qu'on lui donne le début de la réponse (Prompt completion)
    # Mais via LangChain, on simule cela en envoyant une HumanMessage très structurée
    response = llm_classifier.invoke([HumanMessage(content=prompt)])
    
    intent = response.content.strip().lower()
    
    # Nettoyage sévère
    valid_intents = ["devis", "visa", "faq", "annulation", "support", "other"]
    
    final_intent = "other"
    # On cherche le premier mot-clé valide dans la réponse générée (au cas où il a quand même fait une phrase)
    for v_intent in valid_intents:
        if v_intent in intent:
            final_intent = v_intent
            break

    print(f"   -> LLM Output: '{intent}' -> Resolved Intent: {final_intent}")
    return {"intent": final_intent}


def retrieve_context_node(state: AgentState):
    """
    Interroge ChromaDB en fonction de l'intention et du message.
    """
    print("🔍 Node: retrieve_context")
    intent = state.get("intent", "other")
    latest_msg = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    
    # Si c'est juste un bonjour ("other" court), pas besoin de RAG lourd
    if intent == "other" and len(latest_msg.split()) <= 3:
         return {"context": "C'est une salutation, réponds poliment et demande comment tu peux aider."}
         
    # Mapping intent RAG simplifié (les "annulations" pointent vers "administratif")
    rag_intent = intent
    if intent == "annulation":
        rag_intent = "administratif"
    elif intent == "faq" or intent == "support":
        rag_intent = "faq"

    print(f"   -> Exécution RAG pour requête: '{latest_msg}' avec focus: {rag_intent}")
    context = retriever.get_context_for_prompt(latest_msg, intent=rag_intent)
    
    return {"context": context}


def generate_response_node(state: AgentState):
    """
    Génère la réponse finale en injectant le contexte au LLM.
    """
    print("💬 Node: generate_response")
    context = state.get("context", "Le conseiller ne possède pas d'information spécifique pour le moment.")
    
    # Construire le prompt système complet
    sys_prompt = GENERATION_SYSTEM_PROMPT.format(context=context)
    
    # Préparer la liste des messages pour l'appel LLM (System + History)
    messages_for_llm = [SystemMessage(content=sys_prompt)] + state["messages"]
    
    # Appel LLM (temp un peu plus élevée pour être naturel, mais < 0.5 pour rester factuel)
    llm_generator = ChatOllama(model="llama3.2:3b", base_url=settings.OLLAMA_HOST, temperature=0.3)
    response = llm_generator.invoke(messages_for_llm)
    
    final_text = response.content
    print(f"   -> Réponse générée : {final_text[:50]}...")
    
    # On ajoute la réponse générée aux messages (add_messages gérera l'ajout à la liste)
    return {"messages": [AIMessage(content=final_text)], "final_response": final_text}
