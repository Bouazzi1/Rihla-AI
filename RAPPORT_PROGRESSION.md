# Rihla-AI : Rapport d'Avancement du Projet (PFE)

**Objet :** Synthèse technique de la reconstruction du projet "Rihla-AI".
**Statut :** Phases 1 à 4 complétées avec succès.

## 1. Architecture du Système
Le projet a été reconstruit sur une architecture modulaire et asynchrone utilisant les technologies de pointe en IA locale :
- **Backend Core** : FastAPI (Python 3.12) avec SQLAlchemy (Async).
- **Intelligence Artificielle** : LangChain & LangGraph pour l'orchestration des agents.
- **LLM Local** : Llama 3.2 (3B) tournant sur Ollama pour la confidentialité des données.
- **Système RAG (Retrieval Augmented Generation)** : ChromaDB pour l'indexation de la base de connaissances (Visa, FAQ, Programmes).
- **Orchestration** : Docker & n8n pour la glue entre les services WhatsApp, Email et le Core AI.

## 2. Réalisations Techniques (Phases terminées)

### Phase 1 & 2 : Fondations et RAG
- Mise en place d'une base de données PostgreSQL robuste (Clients, Conversations, Messages, Agents, etc.).
- Développement d'un système de génération de données synthétiques (Faker) pour simuler des centaines de clients réels.
- Implémentation d'un pipeline d'ingestion vers une base vectorielle (ChromaDB) permettant à l'IA de consulter les catalogues de voyages et les règles de visa en temps réel.

### Phase 3 : Agent de Communication Intelligent
- Développement d'un graphe d'états (LangGraph) capable de :
  1. **Classifier l'intention** de l'utilisateur (devis, visa, support).
  2. **Récupérer le contexte** spécifique dans la base de connaissances.
  3. **Générer une réponse** naturelle, polie et strictement basée sur les données réelles de l'agence.

### Phase 4 : Intégration Multi-Canal (WhatsApp/Email)
- Couplage avec **WAHA** (WhatsApp HTTP API) pour la communication directe.
- Automatisation des flux via **n8n** :
  - Réception automatique des messages WhatsApp.
  - Traitement par l'IA Rihla Core.
  - Réponse instantanée au client sur le canal d'origine.
- Gestion de l'historique des conversations en base de données pour la continuité du service.

## 3. Prochaines Étapes
1. **Phase 5 : Agent OCR** — Extraction automatique des données depuis les photos de passeports.
2. **Phase 6 : Moteur de Recommandation** — Analyse du profil client pour suggérer les meilleures offres.
3. **Phase 7 : Dashboard Administrateur** — Interface visuelle pour la gestion des programmes par les agents humains de l'agence.

---
*Rapport généré le 13 Mars 2026.*
