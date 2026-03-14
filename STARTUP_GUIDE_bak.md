# 🚀 Rihla-AI : Guide de Démarrage Rapide

Suivez ces étapes à chaque fois que vous redémarrez votre PC pour relancer tout l'écosystème Rihla-AI.

## 1. Démarrer les services Docker
Assurez-vous que Docker Desktop est lancé, puis ouvrez un terminal dans le dossier du projet :
```powershell
docker-compose up -d
```
*Services lancés : n8n (port 5679), WAHA (port 3000), Redis, Mailhog.*

## 2. Vérifier Ollama (Le Cerveau)
Assurez-vous que l'application **Ollama** tourne dans votre barre des tâches. 
L'agent utilise le modèle `llama3.2:3b`. Vous pouvez vérifier qu'il répond via :
```powershell
ollama run llama3.2:3b "Bonjour"
```

## 3. Lancer l'API Rihla-AI (FastAPI)
Ouvrez un nouveau terminal et lancez le serveur d'orchestration :
```powershell
python -m uvicorn communication_server:app --port 8000
```
*Gardez ce terminal ouvert pour voir l'IA réfléchir en temps réel.*

## 4. Vérifier la connexion WhatsApp
1. Allez sur le Dashboard WAHA : [http://localhost:3000](http://localhost:3000)
2. Connectez-vous (User: `admin`, Password: `rihla_admin_2026`, API Key: `68ff5d3b477a4741bd5dbf5345591c21`),ancien Password: `8449ec8e2d96408e8bb38d1c19cbf589`.
3. Vérifiez que la session `default` est bien sur **WORKING** (vert). Si ce n'est pas le cas, scannez à nouveau le QR Code.

## 5. Accéder à n8n
L'interface n8n est disponible ici : [http://localhost:5679](http://localhost:5679)
Vérifiez que le workflow "WhatsApp (WAHA) -> Rihla-AI" est bien en mode **Active**.

---
**Prêt !** Vous pouvez maintenant envoyer des messages sur votre numéro WhatsApp de test pour discuter avec l'IA.
