"""
Rihla-AI — Script d'initialisation de la base de données
Crée toutes les tables définies dans les modèles SQLAlchemy.

Usage:
    python scripts/init_db.py
"""

import sys
import asyncio
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from src.database.base import engine, Base

# Importer tous les modèles pour que Base.metadata les connaisse
from src.database.models import (  # noqa: F401
    Client, Destination, Reservation, Document,
    Conversation, Message, InboxMessage, KnowledgeBase,
)


async def init_database():
    """Crée toutes les tables dans la base de données."""
    print(f"🗄️  Connexion à : {settings.DATABASE_URL}")
    print(f"📋 Tables à créer : {list(Base.metadata.tables.keys())}")

    async with engine.begin() as conn:
        # Créer toutes les tables
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Toutes les tables ont été créées avec succès !")
    print(f"   → {len(Base.metadata.tables)} tables créées")

    # Créer les répertoires de données
    data_dirs = [
        settings.DATA_DIR,
        settings.UPLOADS_DIR,
        settings.KNOWLEDGE_DIR,
        settings.PROGRAMMES_DIR,
        Path(settings.CHROMA_PATH),
    ]
    for d in data_dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"   📁 {d}")

    await engine.dispose()
    print("\n🚀 Rihla-AI est prêt !")


if __name__ == "__main__":
    asyncio.run(init_database())
