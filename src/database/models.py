"""
Rihla-AI — Modèles SQLAlchemy ORM
8 tables : Client, Destination, Reservation, Document,
           Conversation, Message, InboxMessage, KnowledgeBase
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, Date, DateTime,
    ForeignKey, JSON, Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base
import enum


# ═══════════════════════════════════════════
#  Enums
# ═══════════════════════════════════════════

class CanalEnum(str, enum.Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    WEB = "web"


class StatutReservation(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    CONFIRMEE = "confirmee"
    ANNULEE = "annulee"
    TERMINEE = "terminee"


class TypeDocument(str, enum.Enum):
    PASSEPORT = "passeport"
    BILLET = "billet"
    FACTURE = "facture"
    FORMULAIRE = "formulaire"
    AUTRE = "autre"


class TypeDestination(str, enum.Enum):
    OMRA = "omra"
    TOURISME = "tourisme"
    ETUDE = "etude"
    AFFAIRES = "affaires"


class TypeProfil(str, enum.Enum):
    ETUDIANT = "etudiant"
    AFFAIRES = "affaires"
    FAMILLE = "famille"
    AVENTURIER = "aventurier"
    SENIOR = "senior"
    COUPLE = "couple"
    NON_DEFINI = "non_defini"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class StatutConversation(str, enum.Enum):
    ACTIVE = "active"
    FERMEE = "fermee"
    EN_ATTENTE = "en_attente"


class TypeKnowledge(str, enum.Enum):
    FAQ = "faq"
    VISA = "visa"
    PROCEDURE = "procedure"
    INTENT = "intent"
    PROGRAMME = "programme"


# ═══════════════════════════════════════════
#  Modèles
# ═══════════════════════════════════════════

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100))
    prenom: Mapped[str] = mapped_column(String(100))
    telephone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    nationalite: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_naissance: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    type_profil: Mapped[TypeProfil] = mapped_column(
        SAEnum(TypeProfil), default=TypeProfil.NON_DEFINI
    )
    budget_moyen: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    reservations: Mapped[List["Reservation"]] = relationship(back_populates="client")
    documents: Mapped[List["Document"]] = relationship(back_populates="client")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f"<Client {self.prenom} {self.nom} ({self.telephone})>"


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nom: Mapped[str] = mapped_column(String(200))
    pays: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type_destination: Mapped[TypeDestination] = mapped_column(SAEnum(TypeDestination))
    prix_base: Mapped[float] = mapped_column(Float)
    duree_jours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    reservations: Mapped[List["Reservation"]] = relationship(back_populates="destination")

    def __repr__(self) -> str:
        return f"<Destination {self.nom} ({self.pays})>"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    date_depart: Mapped[date] = mapped_column(Date)
    date_retour: Mapped[date] = mapped_column(Date)
    nombre_personnes: Mapped[int] = mapped_column(Integer, default=1)
    prix_total: Mapped[float] = mapped_column(Float)
    statut: Mapped[StatutReservation] = mapped_column(
        SAEnum(StatutReservation), default=StatutReservation.EN_ATTENTE
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    client: Mapped["Client"] = relationship(back_populates="reservations")
    destination: Mapped["Destination"] = relationship(back_populates="reservations")

    def __repr__(self) -> str:
        return f"<Reservation #{self.id} - {self.statut.value}>"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    type_document: Mapped[TypeDocument] = mapped_column(SAEnum(TypeDocument))
    fichier_path: Mapped[str] = mapped_column(String(500))
    donnees_extraites: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ocr_texte: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    client: Mapped["Client"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document {self.type_document.value} - Client #{self.client_id}>"


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    canal: Mapped[CanalEnum] = mapped_column(SAEnum(CanalEnum))
    sujet: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    statut: Mapped[StatutConversation] = mapped_column(
        SAEnum(StatutConversation), default=StatutConversation.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    client: Mapped["Client"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation", order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<Conversation #{self.id} via {self.canal.value}>"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[MessageRole] = mapped_column(SAEnum(MessageRole))
    contenu: Mapped[str] = mapped_column(Text)
    intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entites: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message {self.role.value} @ {self.created_at}>"


class InboxMessage(Base):
    __tablename__ = "inbox_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[CanalEnum] = mapped_column(SAEnum(CanalEnum))
    sender: Mapped[str] = mapped_column(String(255))
    contenu: Mapped[str] = mapped_column(Text)
    media_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<InboxMessage from {self.sender} ({self.source.value})>"


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nom_fichier: Mapped[str] = mapped_column(String(255))
    type_knowledge: Mapped[TypeKnowledge] = mapped_column(SAEnum(TypeKnowledge))
    contenu: Mapped[dict] = mapped_column(JSON)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<KnowledgeBase {self.nom_fichier} v{self.version}>"
