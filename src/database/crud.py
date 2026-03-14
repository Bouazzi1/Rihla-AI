"""
Rihla-AI — Opérations CRUD asynchrones
20+ fonctions pour les 8 tables.
"""

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import (
    Client, Destination, Reservation, Document,
    Conversation, Message, InboxMessage, KnowledgeBase,
    StatutReservation, StatutConversation, CanalEnum,
    TypeDocument, TypeProfil, TypeDestination,
    TypeKnowledge, MessageRole,
)


# ═══════════════════════════════════════════
#  Clients
# ═══════════════════════════════════════════

async def create_client(
    session: AsyncSession,
    nom: str,
    prenom: str,
    telephone: Optional[str] = None,
    email: Optional[str] = None,
    nationalite: Optional[str] = None,
    date_naissance=None,
    type_profil: TypeProfil = TypeProfil.NON_DEFINI,
    budget_moyen: Optional[float] = None,
    notes: Optional[str] = None,
) -> Client:
    client = Client(
        nom=nom,
        prenom=prenom,
        telephone=telephone,
        email=email,
        nationalite=nationalite,
        date_naissance=date_naissance,
        type_profil=type_profil,
        budget_moyen=budget_moyen,
        notes=notes,
    )
    session.add(client)
    await session.flush()
    return client


async def get_client_by_id(session: AsyncSession, client_id: int) -> Optional[Client]:
    result = await session.execute(select(Client).where(Client.id == client_id))
    return result.scalar_one_or_none()


async def get_client_by_phone(session: AsyncSession, telephone: str) -> Optional[Client]:
    result = await session.execute(
        select(Client).where(Client.telephone == telephone)
    )
    return result.scalar_one_or_none()


async def get_client_by_email(session: AsyncSession, email: str) -> Optional[Client]:
    result = await session.execute(
        select(Client).where(Client.email == email)
    )
    return result.scalar_one_or_none()


async def get_all_clients(session: AsyncSession) -> Sequence[Client]:
    result = await session.execute(select(Client).order_by(Client.created_at.desc()))
    return result.scalars().all()


async def update_client(
    session: AsyncSession,
    client_id: int,
    **kwargs,
) -> Optional[Client]:
    kwargs["updated_at"] = datetime.utcnow()
    await session.execute(
        update(Client).where(Client.id == client_id).values(**kwargs)
    )
    await session.flush()
    return await get_client_by_id(session, client_id)


# ═══════════════════════════════════════════
#  Destinations
# ═══════════════════════════════════════════

async def create_destination(
    session: AsyncSession,
    nom: str,
    pays: str,
    type_destination: TypeDestination,
    prix_base: float,
    description: Optional[str] = None,
    duree_jours: Optional[int] = None,
    image_url: Optional[str] = None,
) -> Destination:
    destination = Destination(
        nom=nom,
        pays=pays,
        type_destination=type_destination,
        prix_base=prix_base,
        description=description,
        duree_jours=duree_jours,
        image_url=image_url,
    )
    session.add(destination)
    await session.flush()
    return destination


async def get_destination_by_id(
    session: AsyncSession, destination_id: int
) -> Optional[Destination]:
    result = await session.execute(
        select(Destination).where(Destination.id == destination_id)
    )
    return result.scalar_one_or_none()


async def get_destinations(
    session: AsyncSession,
    type_destination: Optional[TypeDestination] = None,
    active_only: bool = True,
) -> Sequence[Destination]:
    query = select(Destination)
    if active_only:
        query = query.where(Destination.active == True)
    if type_destination:
        query = query.where(Destination.type_destination == type_destination)
    result = await session.execute(query.order_by(Destination.nom))
    return result.scalars().all()


# ═══════════════════════════════════════════
#  Réservations
# ═══════════════════════════════════════════

async def create_reservation(
    session: AsyncSession,
    client_id: int,
    destination_id: int,
    date_depart,
    date_retour,
    prix_total: float,
    nombre_personnes: int = 1,
    notes: Optional[str] = None,
) -> Reservation:
    reservation = Reservation(
        client_id=client_id,
        destination_id=destination_id,
        date_depart=date_depart,
        date_retour=date_retour,
        prix_total=prix_total,
        nombre_personnes=nombre_personnes,
        notes=notes,
    )
    session.add(reservation)
    await session.flush()
    return reservation


async def get_reservations_by_client(
    session: AsyncSession, client_id: int
) -> Sequence[Reservation]:
    result = await session.execute(
        select(Reservation)
        .where(Reservation.client_id == client_id)
        .options(selectinload(Reservation.destination))
        .order_by(Reservation.created_at.desc())
    )
    return result.scalars().all()


async def update_reservation_status(
    session: AsyncSession,
    reservation_id: int,
    statut: StatutReservation,
) -> Optional[Reservation]:
    await session.execute(
        update(Reservation)
        .where(Reservation.id == reservation_id)
        .values(statut=statut, updated_at=datetime.utcnow())
    )
    await session.flush()
    result = await session.execute(
        select(Reservation).where(Reservation.id == reservation_id)
    )
    return result.scalar_one_or_none()


# ═══════════════════════════════════════════
#  Documents
# ═══════════════════════════════════════════

async def create_document(
    session: AsyncSession,
    client_id: int,
    type_document: TypeDocument,
    fichier_path: str,
    donnees_extraites: Optional[dict] = None,
    ocr_texte: Optional[str] = None,
) -> Document:
    document = Document(
        client_id=client_id,
        type_document=type_document,
        fichier_path=fichier_path,
        donnees_extraites=donnees_extraites,
        ocr_texte=ocr_texte,
    )
    session.add(document)
    await session.flush()
    return document


async def get_documents_by_client(
    session: AsyncSession, client_id: int
) -> Sequence[Document]:
    result = await session.execute(
        select(Document)
        .where(Document.client_id == client_id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


# ═══════════════════════════════════════════
#  Conversations
# ═══════════════════════════════════════════

async def create_conversation(
    session: AsyncSession,
    client_id: int,
    canal: CanalEnum,
    sujet: Optional[str] = None,
) -> Conversation:
    conversation = Conversation(
        client_id=client_id,
        canal=canal,
        sujet=sujet,
    )
    session.add(conversation)
    await session.flush()
    return conversation


async def get_conversation(
    session: AsyncSession,
    conversation_id: int,
    with_messages: bool = False,
) -> Optional[Conversation]:
    query = select(Conversation).where(Conversation.id == conversation_id)
    if with_messages:
        query = query.options(selectinload(Conversation.messages))
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_conversations_by_client(
    session: AsyncSession,
    client_id: int,
    statut: Optional[StatutConversation] = None,
) -> Sequence[Conversation]:
    query = select(Conversation).where(Conversation.client_id == client_id)
    if statut:
        query = query.where(Conversation.statut == statut)
    result = await session.execute(query.order_by(Conversation.created_at.desc()))
    return result.scalars().all()


async def get_active_conversation(
    session: AsyncSession,
    client_id: int,
    canal: CanalEnum,
) -> Optional[Conversation]:
    """Trouve la conversation active du client sur un canal donné."""
    result = await session.execute(
        select(Conversation)
        .where(
            Conversation.client_id == client_id,
            Conversation.canal == canal,
            Conversation.statut == StatutConversation.ACTIVE,
        )
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ═══════════════════════════════════════════
#  Messages
# ═══════════════════════════════════════════

async def create_message(
    session: AsyncSession,
    conversation_id: int,
    role: MessageRole,
    contenu: str,
    intent: Optional[str] = None,
    sentiment: Optional[str] = None,
    entites: Optional[dict] = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        contenu=contenu,
        intent=intent,
        sentiment=sentiment,
        entites=entites,
    )
    session.add(message)
    await session.flush()
    return message


async def get_messages_by_conversation(
    session: AsyncSession, conversation_id: int
) -> Sequence[Message]:
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()


# ═══════════════════════════════════════════
#  InboxMessages (messages bruts entrants)
# ═══════════════════════════════════════════

async def create_inbox_message(
    session: AsyncSession,
    source: CanalEnum,
    sender: str,
    contenu: str,
    media_url: Optional[str] = None,
) -> InboxMessage:
    msg = InboxMessage(
        source=source,
        sender=sender,
        contenu=contenu,
        media_url=media_url,
    )
    session.add(msg)
    await session.flush()
    return msg


async def get_unprocessed_inbox_messages(
    session: AsyncSession,
) -> Sequence[InboxMessage]:
    result = await session.execute(
        select(InboxMessage)
        .where(InboxMessage.processed == False)
        .order_by(InboxMessage.created_at.asc())
    )
    return result.scalars().all()


async def mark_inbox_processed(
    session: AsyncSession, message_id: int
) -> Optional[InboxMessage]:
    await session.execute(
        update(InboxMessage)
        .where(InboxMessage.id == message_id)
        .values(processed=True, processed_at=datetime.utcnow())
    )
    await session.flush()
    result = await session.execute(
        select(InboxMessage).where(InboxMessage.id == message_id)
    )
    return result.scalar_one_or_none()


# ═══════════════════════════════════════════
#  KnowledgeBase
# ═══════════════════════════════════════════

async def create_knowledge_entry(
    session: AsyncSession,
    nom_fichier: str,
    type_knowledge: TypeKnowledge,
    contenu: dict,
    description: Optional[str] = None,
) -> KnowledgeBase:
    entry = KnowledgeBase(
        nom_fichier=nom_fichier,
        type_knowledge=type_knowledge,
        contenu=contenu,
        description=description,
    )
    session.add(entry)
    await session.flush()
    return entry


async def get_knowledge_by_type(
    session: AsyncSession,
    type_knowledge: TypeKnowledge,
    active_only: bool = True,
) -> Sequence[KnowledgeBase]:
    query = select(KnowledgeBase).where(
        KnowledgeBase.type_knowledge == type_knowledge
    )
    if active_only:
        query = query.where(KnowledgeBase.active == True)
    result = await session.execute(query.order_by(KnowledgeBase.updated_at.desc()))
    return result.scalars().all()


async def get_all_knowledge(
    session: AsyncSession, active_only: bool = True
) -> Sequence[KnowledgeBase]:
    query = select(KnowledgeBase)
    if active_only:
        query = query.where(KnowledgeBase.active == True)
    result = await session.execute(query.order_by(KnowledgeBase.type_knowledge))
    return result.scalars().all()
