"""
Rihla-AI — Agent Graph (Phase 3)
Assemble les noeuds en un StateGraph LangGraph.
"""

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

from src.agents.state import AgentState
from src.agents.nodes import classify_intent_node, retrieve_context_node, generate_response_node

def build_graph():
    """
    Construit le graphe d'exécution de l'agent.
    """
    workflow = StateGraph(AgentState)
    
    # Ajouter les noeuds
    workflow.add_node("classify", classify_intent_node)
    workflow.add_node("retrieve", retrieve_context_node)
    workflow.add_node("generate", generate_response_node)
    
    # Définir le flux d'exécution
    workflow.add_edge(START, "classify")
    workflow.add_edge("classify", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    # Compiler
    app = workflow.compile()
    return app

class CommunicationAgent:
    """
    Wrapper haut niveau pour appeler le graphe proprement.
    """
    def __init__(self):
        self.app = build_graph()
        
    async def process_message(self, user_message: str, history: list = None) -> tuple[str, str, str]:
        """
        Exécute le graphe sur un nouveau message.
        Retourne (reponse, intent, contexte_utilisé)
        """
        messages = history or []
        messages.append(HumanMessage(content=user_message))
        
        # Initialiser l'état
        print("🚀 Démarrage de l'agent LangGraph...")
        final_state = await self.app.ainvoke({"messages": messages})
        
        return final_state["final_response"], final_state.get("intent", "other"), final_state.get("context", "")

# Instance globale (Singleton)
agent = CommunicationAgent()
