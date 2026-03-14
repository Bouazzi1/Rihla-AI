Atlas-AI — Plan d'implémentation final
Environnement confirmé
Élément	Détail
LLM	llama3.2:3b (2.0 GB) — déjà installé via Ollama
Embeddings	nomic-embed-text (274 MB) — déjà installé
RAM	16 Go
GPU	NVIDIA CUDA (non fonctionnel actuellement)
PostgreSQL	v17 — installé en local (pas Docker)
n8n	Community Edition — déjà installé
WAHA	Déjà configuré pour WhatsApp
Base vectorielle	ChromaDB (local Python, pas de Docker)
Canaux	WhatsApp (WAHA) + Email (Mailhog) — pas de Twilio
Dashboard	Streamlit — en dernière phase
Deadline	~2 mois (mi-mai 2026)
Architecture simplifiée pour PFE
Client WhatsApp/Email
    → WAHA (:3000) / Mailhog (:1025)
    → n8n (:5678) — orchestrateur
    → FastAPI Communication Agent (:8001)
        → Intent Classifier (LLaMA 3.2 3B)
        → NER Extractor
        → Sentiment Analyzer  
        → RAG Retriever (ChromaDB + nomic-embed-text)
        → Response Generator (LLaMA 3.2 3B)
    → PostgreSQL (:5432) — persistance
    → Réponse renvoyée via WAHA/SMTP
IMPORTANT

Avec 16 Go RAM et CUDA non fonctionnel, LLaMA 3.2 3B est le bon choix. Le modèle 7B serait trop lent en CPU. On gardera ChromaDB en local Python (pas de conteneur Docker supplémentaire).

Phases et tâches détaillées
Phase 1 · Fondations (Semaine 1) ⏱️ ~3 jours
#	Tâche	Détail
T1.1	Structure projet	Arborescence pfe/ avec src/, scripts/, tests/, data/, alembic/
T1.2	requirements.txt	SQLAlchemy, Alembic, FastAPI, uvicorn, Pydantic-Settings, asyncpg, chromadb, ollama, httpx, Faker, pytest
T1.3	.env + config.py	Pydantic BaseSettings : DATABASE_URL, OLLAMA_HOST, WAHA_URL, CHROMA_PATH
T1.4	docker-compose.yml	n8n + WAHA + Redis + Mailhog (PostgreSQL est local, pas Docker)
T1.5	Modèles SQLAlchemy	7 tables : Client, Destination, Reservation, Document, Conversation, Message, InboxMessage
T1.6	Alembic	Migrations async configurées
T1.7	CRUD async	20+ fonctions create/get/update
T1.8	init_db.py	Script d'initialisation
T1.9	Tests DB	pytest sur les opérations CRUD
Phase 2 · Données + RAG (Semaine 2) ⏱️ ~3 jours
#	Tâche	Détail
T2.1	Knowledge Base JSON	visa_rules.json, faq.json, procedures.json, intent_examples.json
T2.2	Programmes JSON	omra_packages.json, tourism_packages.json, study_packages.json, activities.json
T2.3	generate_synthetic_data.py	Faker : 60 clients tunisiens, 17 destinations, 150 réservations, 250 messages
T2.4	ChromaDB setup	Client local + embeddings via nomic-embed-text (Ollama)
T2.5	ingest_to_chroma.py	4 collections : conversations, documents, knowledge_base, programmes
T2.6	retriever.py	Recherche multi-collection + build_rag_context()
Phase 3 · Agent de Communication (Semaines 3-4) ⏱️ ~5 jours
#	Tâche	Détail
T3.1	llm_service.py	Wrapper Ollama : generate(), classify(), extract(), embed()
T3.2	intent_classifier.py	Zero-Shot via LLaMA 3.2 3B, 6 catégories
T3.3	ner_extractor.py	Regex + Few-Shot LLM (dates, destinations, budget, nb personnes)
T3.4	sentiment_analyzer.py	Keywords + LLM, détection urgence
T3.5	response_generator.py	RAG context + LLM → réponse naturelle en français
T3.6	agent.py	Pipeline : identifier client → classify → NER → sentiment → RAG → respond → store DB
T3.7	communication_server.py	FastAPI port 8001 : /process_message, /whatsapp, /health
T3.8	Tests NLP	Tests unitaires du pipeline complet
Phase 4 · Intégration WhatsApp + Email (Semaine 4) ⏱️ ~2 jours
#	Tâche	Détail
T4.1	Workflow n8n WhatsApp	WAHA Webhook → HTTP Request (API 8001) → WAHA Reply
T4.2	Workflow n8n Email	Mailhog IMAP → HTTP Request (API 8001) → SMTP Reply
T4.3	Sauvegarde conversations	Noeud n8n PostgreSQL pour logger chaque échange
T4.4	Test E2E WhatsApp	Message → LLaMA réponse → Reply sur WhatsApp
T4.5	Test E2E Email	Email → LLaMA réponse → Reply par email
Phase 5 · Agent OCR (Semaines 5-6) ⏱️ ~4 jours
#	Tâche	Détail
T5.1	Installer PaddleOCR	Support arabe + français + latin
T5.2	FastAPI OCR service	Port 8002 : /ocr endpoint, upload image → JSON
T5.3	Parser MRZ	Extraction structurée des passeports (regex + passporteye)
T5.4	Structureur JSON	Passeport → {nom, prénom, nationalité, date_naissance, date_expiration}
T5.5	Intégration n8n	Photo WhatsApp → OCR service → stockage DB + MinIO
T5.6	Tests OCR	Tests avec exemples de documents (passeport, billet, facture)
Phase 6 · Moteur de Recommandation (Semaines 6-7) ⏱️ ~4 jours
#	Tâche	Détail
T6.1	Profilage client	Agrégation signaux : OCR + conversation + formulaire + historique
T6.2	Classification profil	LLM classifie : étudiant, affaires, famille, aventurier, senior, couple
T6.3	Indexation ChromaDB	Activités, hébergements, sorties groupes → vecteurs
T6.4	Scoring multi-critères	score = f(profil × activité × budget × saison × groupe)
T6.5	Génération programme	LLM → programme séjour J1→Jn personnalisé
T6.6	PDF Gotenberg	HTML template → PDF via Gotenberg Docker
T6.7	Intégration n8n	Recommandation → PDF → envoi WhatsApp/Email
Phase 7 · Dashboard Streamlit (Semaine 8) ⏱️ ~3 jours
#	Tâche	Détail
T7.1	Setup multi-pages	Architecture Streamlit avec sidebar navigation
T7.2	Page Dashboard	KPIs, graphiques clients, réservations, revenus
T7.3	Page Messages	Historique conversations avec filtres
T7.4	Page Documents	Résultats OCR, documents scannés
T7.5	Page Recommandations	Programmes générés, profils clients
Phase 8 · Finalisation (Semaine 9) ⏱️ ~2 jours
#	Tâche	Détail
T8.1	Tests E2E complets	Tous les flux de bout en bout
T8.2	Optimisation	Prompts, usage mémoire, temps de réponse
T8.3	Documentation	README, docstrings, architecture docs
T8.4	Script de démo	Scénario complet pour la soutenance
T8.5	Présentation PFE	Slides + démo live
Planning prévisionnel (~9 semaines sur 8 disponibles)
Mars S3-S4 │ Phase 1 (Fondations) + Phase 2 (Données + RAG)
Avril S1   │ Phase 3 (Agent Communication)
Avril S2   │ Phase 3 (suite) + Phase 4 (WhatsApp/Email)
Avril S3   │ Phase 5 (OCR)
Avril S4   │ Phase 5 (suite) + Phase 6 (Recommandation)
Mai S1     │ Phase 6 (suite) + Phase 7 (Dashboard)
Mai S2     │ Phase 7 (suite) + Phase 8 (Finalisation)
Mai S3     │ Buffer (retards/démo) 🎯 Soutenance
TIP

Le buffer d'une semaine en fin de planning permet d'absorber les retards éventuels. Les phases sont ordonnées par dépendance : chaque phase dépend de la précédente.

Vérification
Par phase
Phase 1 : python scripts/init_db.py + pytest tests/test_database.py
Phase 2 : python scripts/ingest_to_chroma.py → vérifier 4 collections créées
Phase 3 : curl http://localhost:8001/health + tester /process_message
Phase 4 : Envoyer un WhatsApp → recevoir une réponse IA
Phase 5 : curl -X POST http://localhost:8002/ocr -F "file=@passport.jpg"
Phase 6 : Demander un voyage → recevoir un PDF personnalisé
Phase 7 : Ouvrir Streamlit → voir les données en temps réel