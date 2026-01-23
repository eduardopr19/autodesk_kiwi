# 🗺️ Roadmap - AutoDesk Kiwi

Ce document trace les grandes lignes des évolutions futures pour AutoDesk Kiwi.

## 📅 Court Terme (Q1)

- [ ] **Amélioration de l'UI/UX** :
  - [ ] Ajouter des animations de transition plus fluides entre les vues.
  - [ ] Implémenter un mode "Focus" pour masquer les distractions.
- [ ] **Fonctionnalités Tâches** :
  - [ ] Ajouter des dates d'échéance (Due Dates).
  - [ ] Support des sous-tâches.
  - [ ] Catégories ou Tags personnalisables.
- **Tech** :
  - [ ] Ajouter des tests unitaires pour le backend (`pytest`).
  - [ ] Mettre en place un linter/formatter (`ruff` ou `black`).

## 📅 Moyen Terme (Q2)

- [ ] **Authentification & Multi-utilisateurs** :
  - [ ] Système de login/register (JWT).
  - [ ] Sécurisation des endpoints API.
- [ ] **Synchronisation Cloud** :
  - [ ] Possibilité de sauvegarder la base de données sur un cloud (ex: S3, Google Drive).
- [ ] **Personnalisation** :
  - [ ] Thèmes personnalisables (couleurs, polices).
  - [ ] Widgets configurables sur le dashboard.

## 📅 Long Terme (Q3+)

- [ ] **Notifications Push** :
  - [ ] Rappels de tâches et d'événements sur le navigateur/mobile.
- [ ] **Intégrations Avancées** :
  - [ ] Connexion directe aux API Google Calendar / Outlook Calendar (lecture/écriture).
  - [ ] Intégration Notion ou Obsidian.
- [ ] **Application Mobile** :
  - [ ] Envisager une PWA (Progressive Web App) ou une app native (React Native/Flutter).
- [ ] **Dockerisation** :
  - [ ] Créer un `Dockerfile` et `docker-compose.yml` pour un déploiement facile.

## 💡 Idées en Vrac

- Mode "Sombre/Clair" automatique selon le système.
- Commande vocale pour ajouter des tâches.
- Analyse de productivité (graphiques d'avancement).
