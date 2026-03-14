"""
Rihla-AI — Générateur de données synthétiques (Phase 2)
Génère des clients, destinations, réservations, documents et conversations
dans la base de données pour avoir un environnement complet à tester.
"""

import sys
import asyncio
import random
from pathlib import Path
from datetime import datetime, date, timedelta

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Config paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.base import engine, async_sessionmaker
from src.database.models import (
    Client, Destination, Reservation, Conversation, Message,
    TypeProfil, TypeDestination, StatutReservation, CanalEnum,
    StatutConversation, MessageRole, TypeDocument, Document
)

fake = Faker('fr_FR')

# --- Données de référence ---

DESTINATIONS_DATA = [
    ("Omra Économique", "Arabie Saoudite", TypeDestination.OMRA, 3200.0, 15),
    ("Omra VIP", "Arabie Saoudite", TypeDestination.OMRA, 5500.0, 10),
    ("Istanbul Magique", "Turquie", TypeDestination.TOURISME, 1500.0, 7),
    ("Antalya Séjour Balnéaire", "Turquie", TypeDestination.TOURISME, 1800.0, 7),
    ("Aventure Thaïlandaise", "Thaïlande", TypeDestination.TOURISME, 3800.0, 10),
    ("Paris Romantique", "France", TypeDestination.TOURISME, 2200.0, 5),
    ("Circuit Andalousie", "Espagne", TypeDestination.TOURISME, 2500.0, 8),
    ("Études en France - Accompagnement", "France", TypeDestination.ETUDE, 900.0, 30),
    ("Visa Affaires Dubaï", "Emirats", TypeDestination.AFFAIRES, 1200.0, 5),
]

INTENTS = ["devis", "reservation", "information", "support", "paiement"]
SENTIMENTS = ["positif", "neutre", "negatif"]


async def init_destinations(session: AsyncSession):
    """Crée les destinations de base si elles n'existent pas."""
    print("🌍 Génération des destinations...")
    existing = await session.execute(select(func.count(Destination.id)))
    if existing.scalar() > 0:
        print("   Destinations déjà présentes, on skip.")
        return

    destinations = []
    for nom, pays, t, prix, duree in DESTINATIONS_DATA:
        dest = Destination(
            nom=nom, pays=pays, type_destination=t,
            prix_base=prix, duree_jours=duree
        )
        session.add(dest)
        destinations.append(dest)
    
    await session.commit()
    print(f"   ✅ {len(destinations)} destinations créées.")


async def generate_clients(session: AsyncSession, count: int = 50):
    """Génère un nombre donné de clients fictifs."""
    print(f"👥 Génération de {count} clients...")
    profils = list(TypeProfil)
    clients_crees = 0

    for _ in range(count):
        # 80% de tunisiens
        nationalite = "Tunisienne" if random.random() < 0.8 else fake.country()
        
        # Date de naissance (entre 18 et 75 ans)
        age = random.randint(18, 75)
        dob = fake.date_of_birth(minimum_age=18, maximum_age=75)

        client = Client(
            nom=fake.last_name(),
            prenom=fake.first_name(),
            telephone=f"+216{random.randint(2,9)}{random.randint(1000000,9999999)}",
            email=fake.unique.email(),
            nationalite=nationalite,
            date_naissance=dob,
            type_profil=random.choice(profils),
            budget_moyen=random.uniform(1000.0, 6000.0),
        )
        session.add(client)
        clients_crees += 1
        
        if clients_crees % 10 == 0:
            await session.commit()
            
    await session.commit()
    print(f"   ✅ {clients_crees} clients générés.")


async def generate_reservations(session: AsyncSession, count: int = 150):
    """Associe aléatoirement des réservations aux clients existants."""
    print(f"✈️ Génération de {count} réservations...")
    
    # Récupérer clients et destinations
    clients_res = await session.execute(select(Client.id))
    client_ids = [row[0] for row in clients_res.fetchall()]
    
    dests_res = await session.execute(select(Destination))
    destinations = dests_res.scalars().all()

    if not client_ids or not destinations:
        print("   ❌ Erreur : Clients ou Destinations manquants.")
        return

    statuts = list(StatutReservation)

    for i in range(count):
        client_id = random.choice(client_ids)
        dest = random.choice(destinations)
        
        nb_pers = random.randint(1, 4)
        prix_total = dest.prix_base * nb_pers * random.uniform(0.9, 1.2)
        
        # Départ entre -60 et +90 jours
        days_offset = random.randint(-60, 90)
        date_depart = date.today() + timedelta(days=days_offset)
        date_retour = date_depart + timedelta(days=dest.duree_jours or 7)

        resa = Reservation(
            client_id=client_id,
            destination_id=dest.id,
            date_depart=date_depart,
            date_retour=date_retour,
            nombre_personnes=nb_pers,
            prix_total=round(prix_total, 2),
            statut=random.choice(statuts)
        )
        session.add(resa)
        
    await session.commit()
    print(f"   ✅ {count} réservations générées.")


async def generate_conversations_and_messages(session: AsyncSession, count: int = 100):
    """Génère des historiques de conversations."""
    print(f"💬 Génération de {count} conversations avec messages...")
    
    clients_res = await session.execute(select(Client.id))
    client_ids = [row[0] for row in clients_res.fetchall()]

    for _ in range(count):
        client_id = random.choice(client_ids)
        canal = random.choice([CanalEnum.WHATSAPP, CanalEnum.WHATSAPP, CanalEnum.EMAIL])  # Plus de WA
        
        conv = Conversation(
            client_id=client_id,
            canal=canal,
            sujet=fake.sentence(nb_words=5),
            statut=random.choice(list(StatutConversation))
        )
        session.add(conv)
        await session.flush()  # Pour avoir l'ID de la conv
        
        # Ajouter 2 à 8 messages
        nb_messages = random.randint(2, 8)
        
        for i in range(nb_messages):
            # Alternance Utilisateur / IA
            role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
            
            intent = random.choice(INTENTS) if role == MessageRole.USER else None
            sentiment = random.choice(SENTIMENTS) if role == MessageRole.USER else None
            
            msg = Message(
                conversation_id=conv.id,
                role=role,
                contenu=fake.text(max_nb_chars=120),
                intent=intent,
                sentiment=sentiment
            )
            session.add(msg)
            
    await session.commit()
    print(f"   ✅ {count} conversations + messages générés.")


async def main():
    print("🚀 Début de la génération de données synthétiques...")
    
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        await init_destinations(session)
        await generate_clients(session, 60)
        await generate_reservations(session, 150)
        await generate_conversations_and_messages(session, 80)
        
    await engine.dispose()
    print("🎉 Terminée avec succès ! La base est peuplée.")


if __name__ == "__main__":
    asyncio.run(main())
