"""
Rihla-AI — Communication Server (Phase 3)
Interface FastAPI pour recevoir et traiter les messages via n8n.
"""

from pathlib import Path
from datetime import datetime
import sys

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Config paths
sys.path.insert(0, str(Path(__file__).parent))

from src.database.base import get_session
from src.database.models import (
    Client, Conversation, Message, 
    CanalEnum, StatutConversation, MessageRole, TypeProfil
)
from src.agents.graph import agent

app = FastAPI(title="Rihla-AI Communication API")

# Modèles Pydantic pour la requête/réponse

class ChatRequest(BaseModel):
    sender: str              # Téléphone ou Email
    message: str             # Le contenu du message
    canal: str               # "WHATSAPP" ou "EMAIL"
    nom_client: str = ""     # Optionnel
    prenom_client: str = ""  # Optionnel

class ChatResponse(BaseModel):
    reply: str
    intent: str
    
# Logique métier asynchrone

async def handle_chat(request: ChatRequest, db: AsyncSession) -> ChatResponse:
    """
    Processus complet :
    1. Trouver ou créer le client
    2. Trouver ou créer la conversation
    3. Charger l'historique
    4. Appeler l'agent LangGraph
    5. Sauvegarder les messages
    """
    canal_enum = CanalEnum[request.canal.upper()]
    
    # 1. Gestion du Client
    client = None
    if canal_enum == CanalEnum.WHATSAPP:
        result = await db.execute(select(Client).where(Client.telephone == request.sender))
        client = result.scalar_one_or_none()
    elif canal_enum == CanalEnum.EMAIL:
        result = await db.execute(select(Client).where(Client.email == request.sender))
        client = result.scalar_one_or_none()
        
    if not client:
        client = Client(
            nom=request.nom_client or "Inconnu",
            prenom=request.prenom_client or "Client",
            telephone=request.sender if canal_enum == CanalEnum.WHATSAPP else None,
            email=request.sender if canal_enum == CanalEnum.EMAIL else None,
            type_profil=TypeProfil.NON_DEFINI
        )
        db.add(client)
        await db.flush()
        
    # 2. Gestion de la Conversation
    result = await db.execute(
        select(Conversation)
        .where(Conversation.client_id == client.id)
        .where(Conversation.canal == canal_enum)
        .where(Conversation.statut == StatutConversation.ACTIVE)
        .order_by(Conversation.created_at.desc())
    )
    conv = result.scalars().first()
    
    if not conv:
        conv = Conversation(
            client_id=client.id,
            canal=canal_enum,
            sujet=f"Nouvelle demande ({request.message[:20]}...)",
            statut=StatutConversation.ACTIVE
        )
        db.add(conv)
        await db.flush()
        
    # 4. Appeler l'agent
    print(f"📩 Message reçu de {client.prenom} {client.nom} ({request.canal}) : {request.message}")
    reply_text, intent, context = await agent.process_message(user_message=request.message, history=[])
    
    # 5. Sauvegarder
    msg_user = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        contenu=request.message,
        intent=intent
    )
    db.add(msg_user)
    
    msg_agent = Message(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        contenu=reply_text,
    )
    db.add(msg_agent)
    
    conv.updated_at = datetime.utcnow()
    await db.commit()
    
    return ChatResponse(reply=reply_text, intent=intent)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_session)):
    try:
        if request.canal.upper() not in ["WHATSAPP", "EMAIL", "WEB"]:
            raise HTTPException(status_code=400, detail="Invalid canal. Use WHATSAPP, EMAIL or WEB.")
        return await handle_chat(request, db)
    except Exception as e:
        await db.rollback()
        print(f"❌ Erreur Serveur: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Rihla-AI API"}

if __name__ == "__main__":
    uvicorn.run("communication_server:app", host="0.0.0.0", port=8000, reload=True)
