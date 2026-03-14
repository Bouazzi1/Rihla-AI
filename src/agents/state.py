"""
Rihla-AI — Agent State (Phase 3)
Définition de l'état du graphe LangGraph pour l'agent de communication.
"""

from typing import Annotated, TypedDict, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    État du graphe LangGraph représentant une interaction utilisateur.
    """
    # Historique de la conversation (ajoute les nouveaux messages à la liste)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Contexte métier DB
    client_id: Optional[int]
    conversation_id: Optional[int]
    canal: str # WHATSAPP, EMAIL, etc.
    
    # Données extraites par le graphe
    intent: Optional[str]      # faq, visa, reservation, devis, support, other
    context: Optional[str]     # Texte brut récupéré du RAG
    
    # Réponse finale (pour export DB)
    final_response: Optional[str]
