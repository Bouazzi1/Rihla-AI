# Rihla-AI — Guide de Configuration n8n & WhatsApp

Ce guide vous explique comment activer l'intégration WhatsApp via WAHA et n8n.

## 1. Démarrer les services
Assurez-vous que tous les conteneurs (n8n, WAHA, Redis, Mailhog) sont lancés :
```bash
docker-compose up -d
```
Assurez-vous également que l'API FastAPI est lancée localement (port 8000) :
```bash
python -m uvicorn communication_server:app --port 8000
```

## 2. Connecter votre numéro WhatsApp (WAHA)
1. Ouvrez l'interface WAHA : [http://localhost:3000](http://localhost:3000) (Username : `admin` / Password : `rihla_admin_2026`)

2. Connectez le Dashboard à votre serveur WAHA :
   - **Name** : `WAHA`
   - **API URL** : `http://localhost:3000`
   - **API Key** : `68ff5d3b477a4741bd5dbf5345591c21`
3. Allez dans l'onglet **Sessions** (menu de gauche).
4. Cliquez sur **+ Add Session**. Entrez `default` comme nom de session et validez.
5. La session va apparaître avec le statut `STARTING`. Attendez un instant, puis cliquez sur l'icône de l'appareil photo/œil pour afficher le **QR Code**.
6. Ouvrez WhatsApp sur votre téléphone > "Appareils connectés" > "Connecter un appareil", et **scannez le QR code**. Le statut de la session passera à `WORKING`.

## 3. Importer les Workflows dans n8n
1. Ouvrez l'interface n8n : [http://localhost:5679](http://localhost:5679)
2. Cliquez sur **Workflows** (dans le menu de gauche) puis **Add workflow**.
3. En haut à droite, cliquez sur les trois petits points `...` > **Import from File**.
4. Sélectionnez le fichier `n8n/whatsapp_workflow.json`.
5. Sauvegardez le workflow, et surtout, **activez-le** (toggle en haut à droite sur "Active").
6. *(Optionnel)* Faites la même chose avec `n8n/email_workflow.json`.

## 4. Configurer le Webhook dans WAHA
Pour que WAHA prévienne n8n quand un message arrive, on doit lui indiquer l'URL du Webhook de n8n.
1. Allez dans l'interface Swagger de WAHA : [http://localhost:3000/#/Webhooks](http://localhost:3000/#/Webhooks).
2. Cherchez l'API webhooks et configurez-la pour envoyer les événements `message` vers :
`http://n8n:5678/webhook/waha`

## 5. Test de bout en bout
Envoyez un message WhatsApp au numéro que vous avez connecté à l'étape 2 (demandez un ami de vous envoyer "Je veux voir l'offre Omra VIP").
L'agent Rihla-AI lira le message, l'enregistrera en DB, trouvera le bon contexte, et renverra la réponse directement sur la conversation WhatsApp !
