# 🥝 AutoDesk Kiwi

AutoDesk Kiwi est un hub personnel de productivité et d'automatisation conçu pour centraliser vos tâches, votre agenda et les informations essentielles de votre journée.

## 🚀 Fonctionnalités

- **Tableau de bord personnel** :
  - Citation du jour
  - Prochain événement à venir
  - Météo en temps réel
  - Résumé des emails non lus (Proton, Outlook)
- **Gestion de tâches (To-Do List)** :
  - Création, modification et suppression de tâches
  - Priorisation (Low, Normal, High)
  - Filtrage par statut et priorité
  - Tri par date, priorité ou titre
- **Météo détaillée** :
  - Prévisions horaires et journalières
- **Interface réactive** :
  - Design moderne et sombre (Dark Mode)
  - Compatible mobile et desktop

## 🛠️ Stack Technique

- **Backend** : Python, FastAPI, SQLite
- **Frontend** : HTML5, CSS3 (Vanilla), Alpine.js
- **Base de données** : SQLite (local)

## 📦 Installation

### Prérequis

- Python 3.12+
- Un navigateur web moderne

### Installation du Backend

1. Naviguez dans le dossier `api` :
   ```bash
   cd api
   ```

2. Créez un environnement virtuel (recommandé) :
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez les variables d'environnement :
   ```bash
   cp .env.example .env
   ```
   Éditez le fichier `.env` et remplissez vos valeurs (notamment `HYPERPLANNING_URL` si vous utilisez Hyperplanning).

5. Lancez le serveur :
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Le serveur sera accessible sur `http://127.0.0.1:8000`.

### Utilisation du Frontend

1. Ouvrez simplement le fichier `web/index.html` dans votre navigateur.
2. L'application se connectera automatiquement à l'API locale.

## 📂 Structure du Projet

```
autodesk_kiwi/
├── api/                 # Backend FastAPI
│   ├── routes/          # Endpoints API (tasks, meta, integrations)
│   ├── main.py          # Point d'entrée de l'application
│   ├── models.py        # Modèles de données (Pydantic/SQLAlchemy)
│   ├── db.py            # Gestion de la base de données
│   └── ...
├── web/                 # Frontend
│   └── index.html       # Application unique (SPA) avec Alpine.js
└── cmd                  # Script de lancement rapide (Windows)
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est sous licence MIT.
