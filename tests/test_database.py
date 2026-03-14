"""
Rihla-AI — Tests de la couche base de données
Teste les opérations CRUD sur toutes les tables.

Usage:
    pytest tests/test_database.py -v
"""

import sys
from pathlib import Path
from datetime import date, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from src.database.base import Base
from src.database.models import (
    CanalEnum, StatutReservation, TypeDocument,
    TypeDestination, TypeProfil, MessageRole,
    TypeKnowledge, StatutConversation,
)
from src.database.crud import (
    # Clients
    create_client, get_client_by_id, get_client_by_phone,
    get_all_clients, update_client,
    # Destinations
    create_destination, get_destination_by_id, get_destinations,
    # Réservations
    create_reservation, get_reservations_by_client, update_reservation_status,
    # Documents
    create_document, get_documents_by_client,
    # Conversations
    create_conversation, get_conversation, get_conversations_by_client,
    # Messages
    create_message, get_messages_by_conversation,
    # InboxMessages
    create_inbox_message, get_unprocessed_inbox_messages, mark_inbox_processed,
    # KnowledgeBase
    create_knowledge_entry, get_knowledge_by_type,
)


# ── Fixtures ──

@pytest_asyncio.fixture(scope="session")
async def engine():
    """Crée un engine de test partagé entre tous les tests, avec NullPool pour éviter les conflits async."""
    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
         await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture()
async def session(engine):
    """Fournit une session isolée pour chaque test."""
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        # On utilise une transaction imbriquée (SAVEPOINT) pour chaque test
        await session.begin()
        yield session
        await session.rollback()


# ═══════════════════════════════════════════
#  Tests Clients
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_client(session: AsyncSession):
    client = await create_client(
        session,
        nom="Ben Ali",
        prenom="Mohamed",
        telephone="+21698000001",
        email="mohamed@test.tn",
        nationalite="Tunisienne",
    )
    assert client.id is not None
    assert client.nom == "Ben Ali"
    assert client.prenom == "Mohamed"
    assert client.type_profil == TypeProfil.NON_DEFINI


@pytest.mark.asyncio
async def test_get_client_by_phone(session: AsyncSession):
    await create_client(
        session, nom="Trabelsi", prenom="Fatma",
        telephone="+21698000002",
    )
    found = await get_client_by_phone(session, "+21698000002")
    assert found is not None
    assert found.prenom == "Fatma"


@pytest.mark.asyncio
async def test_get_client_by_id(session: AsyncSession):
    client = await create_client(
        session, nom="Gharbi", prenom="Sami",
        telephone="+21698000003",
    )
    found = await get_client_by_id(session, client.id)
    assert found is not None
    assert found.nom == "Gharbi"


@pytest.mark.asyncio
async def test_update_client(session: AsyncSession):
    client = await create_client(
        session, nom="Hamdi", prenom="Amine",
        telephone="+21698000004",
    )
    updated = await update_client(
        session, client.id, type_profil=TypeProfil.ETUDIANT
    )
    assert updated.type_profil == TypeProfil.ETUDIANT


@pytest.mark.asyncio
async def test_get_all_clients(session: AsyncSession):
    await create_client(session, nom="A", prenom="A1", telephone="+21600000010")
    await create_client(session, nom="B", prenom="B1", telephone="+21600000011")
    clients = await get_all_clients(session)
    assert len(clients) >= 2


# ═══════════════════════════════════════════
#  Tests Destinations
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_destination(session: AsyncSession):
    dest = await create_destination(
        session,
        nom="La Mecque - Omra Standard",
        pays="Arabie Saoudite",
        type_destination=TypeDestination.OMRA,
        prix_base=3500.0,
        duree_jours=14,
    )
    assert dest.id is not None
    assert dest.prix_base == 3500.0


@pytest.mark.asyncio
async def test_get_destinations_by_type(session: AsyncSession):
    await create_destination(
        session, nom="Istanbul", pays="Turquie",
        type_destination=TypeDestination.TOURISME, prix_base=1200.0,
    )
    await create_destination(
        session, nom="Omra VIP", pays="Arabie Saoudite",
        type_destination=TypeDestination.OMRA, prix_base=6000.0,
    )
    tourisme = await get_destinations(session, type_destination=TypeDestination.TOURISME)
    assert all(d.type_destination == TypeDestination.TOURISME for d in tourisme)


# ═══════════════════════════════════════════
#  Tests Réservations
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_reservation(session: AsyncSession):
    client = await create_client(
        session, nom="Rezgui", prenom="Yassine",
        telephone="+21698000110",
    )
    dest = await create_destination(
        session, nom="Marrakech", pays="Maroc",
        type_destination=TypeDestination.TOURISME, prix_base=800.0,
    )
    reservation = await create_reservation(
        session,
        client_id=client.id,
        destination_id=dest.id,
        date_depart=date.today() + timedelta(days=30),
        date_retour=date.today() + timedelta(days=37),
        prix_total=1600.0,
        nombre_personnes=2,
    )
    assert reservation.id is not None
    assert reservation.statut == StatutReservation.EN_ATTENTE


@pytest.mark.asyncio
async def test_update_reservation_status(session: AsyncSession):
    client = await create_client(
        session, nom="Test", prenom="Resa",
        telephone="+21698000111",
    )
    dest = await create_destination(
        session, nom="Paris", pays="France",
        type_destination=TypeDestination.TOURISME, prix_base=1500.0,
    )
    resa = await create_reservation(
        session, client_id=client.id, destination_id=dest.id,
        date_depart=date.today(), date_retour=date.today() + timedelta(days=7),
        prix_total=1500.0,
    )
    updated = await update_reservation_status(
        session, resa.id, StatutReservation.CONFIRMEE
    )
    assert updated.statut == StatutReservation.CONFIRMEE


# ═══════════════════════════════════════════
#  Tests Documents
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_document(session: AsyncSession):
    client = await create_client(
        session, nom="Doc", prenom="Test",
        telephone="+21698000120",
    )
    doc = await create_document(
        session,
        client_id=client.id,
        type_document=TypeDocument.PASSEPORT,
        fichier_path="data/uploads/passport_001.jpg",
        donnees_extraites={"nom": "Doc", "prenom": "Test", "nationalite": "TN"},
    )
    assert doc.id is not None
    assert doc.donnees_extraites["nationalite"] == "TN"


@pytest.mark.asyncio
async def test_get_documents_by_client(session: AsyncSession):
    client = await create_client(
        session, nom="Multi", prenom="Doc",
        telephone="+21698000121",
    )
    await create_document(
        session, client_id=client.id,
        type_document=TypeDocument.PASSEPORT, fichier_path="p1.jpg",
    )
    await create_document(
        session, client_id=client.id,
        type_document=TypeDocument.BILLET, fichier_path="b1.jpg",
    )
    docs = await get_documents_by_client(session, client.id)
    assert len(docs) == 2


# ═══════════════════════════════════════════
#  Tests Conversations + Messages
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_conversation_with_messages(session: AsyncSession):
    client = await create_client(
        session, nom="Chat", prenom="Test",
        telephone="+21698000130",
    )
    conv = await create_conversation(
        session, client_id=client.id,
        canal=CanalEnum.WHATSAPP, sujet="Demande de devis Omra",
    )
    assert conv.statut == StatutConversation.ACTIVE

    # Ajouter des messages
    msg1 = await create_message(
        session, conversation_id=conv.id,
        role=MessageRole.USER,
        contenu="Bonjour, je veux un devis pour la Omra en famille",
        intent="devis",
        sentiment="positif",
    )
    msg2 = await create_message(
        session, conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        contenu="Bonjour ! Bien sûr, combien de personnes êtes-vous ?",
    )

    messages = await get_messages_by_conversation(session, conv.id)
    assert len(messages) == 2
    assert messages[0].role == MessageRole.USER
    assert messages[1].role == MessageRole.ASSISTANT


@pytest.mark.asyncio
async def test_get_conversation_with_messages(session: AsyncSession):
    client = await create_client(
        session, nom="Conv", prenom="Full",
        telephone="+21698000131",
    )
    conv = await create_conversation(
        session, client_id=client.id,
        canal=CanalEnum.EMAIL,
    )
    await create_message(
        session, conversation_id=conv.id,
        role=MessageRole.USER, contenu="Hello",
    )
    loaded = await get_conversation(session, conv.id, with_messages=True)
    assert loaded is not None
    assert len(loaded.messages) == 1


# ═══════════════════════════════════════════
#  Tests InboxMessages
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_inbox_message_lifecycle(session: AsyncSession):
    msg = await create_inbox_message(
        session,
        source=CanalEnum.WHATSAPP,
        sender="+21698999999",
        contenu="Salam, je cherche un voyage à Istanbul",
    )
    assert msg.processed is False

    # Récupérer les non-traités
    unprocessed = await get_unprocessed_inbox_messages(session)
    assert any(m.id == msg.id for m in unprocessed)

    # Marquer comme traité
    processed = await mark_inbox_processed(session, msg.id)
    assert processed.processed is True
    assert processed.processed_at is not None


# ═══════════════════════════════════════════
#  Tests KnowledgeBase
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_knowledge_base_crud(session: AsyncSession):
    entry = await create_knowledge_entry(
        session,
        nom_fichier="faq.json",
        type_knowledge=TypeKnowledge.FAQ,
        contenu={"questions": [
            {"q": "Quels sont vos horaires ?", "a": "8h-18h du lundi au samedi."}
        ]},
        description="FAQ de l'agence Rihla",
    )
    assert entry.id is not None
    assert entry.version == 1

    faqs = await get_knowledge_by_type(session, TypeKnowledge.FAQ)
    assert len(faqs) >= 1
    assert faqs[0].nom_fichier == "faq.json"
