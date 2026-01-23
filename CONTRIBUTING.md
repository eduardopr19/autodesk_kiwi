# 🤝 Guide de Contribution

Merci de votre intérêt pour contribuer à AutoDesk Kiwi ! Voici comment vous pouvez aider.

## 📋 Comment contribuer

### 1. Fork et Clone

```bash
# Fork le projet sur GitHub, puis :
git clone https://github.com/VOTRE_USERNAME/autodesk_kiwi.git
cd autodesk_kiwi
```

### 2. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### 3. Configuration de l'environnement

```bash
# Backend
cd api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditez .env avec vos valeurs
```

### 4. Faire vos modifications

- Suivez le style de code existant
- Ajoutez des tests si possible
- Commentez le code complexe
- Utilisez des messages de commit clairs

### 5. Tester vos changements

```bash
# Lancer l'API
cd api
uvicorn main:app --reload

# Ouvrir web/index.html dans votre navigateur
```

### 6. Commit et Push

```bash
git add .
git commit -m "feat: description de votre fonctionnalité"
git push origin feature/ma-nouvelle-fonctionnalite
```

### 7. Créer une Pull Request

Allez sur GitHub et créez une Pull Request vers la branche `main`.

## 📝 Standards de Code

### Python (Backend)

- Python 3.12+
- Type hints partout
- Docstrings pour les fonctions publiques
- Utilisez `logger` au lieu de `print()`
- Suivez PEP 8

### JavaScript (Frontend)

- Code lisible et commenté
- Évitez les modifications globales
- Testez sur plusieurs navigateurs

### Commits

Format recommandé :
```
feat: ajoute nouvelle fonctionnalité
fix: corrige bug dans X
docs: met à jour documentation
refactor: améliore code de Y
test: ajoute tests pour Z
```

## 🐛 Signaler un Bug

Ouvrez une issue avec :
- Description claire du problème
- Steps pour reproduire
- Comportement attendu vs observé
- Captures d'écran si applicable
- Environnement (OS, Python version, navigateur)

## 💡 Proposer une Fonctionnalité

Ouvrez une issue avec :
- Description de la fonctionnalité
- Cas d'usage
- Exemples d'interface si applicable

## ✅ Checklist avant PR

- [ ] Le code fonctionne localement
- [ ] Pas de secrets/tokens dans le code
- [ ] Messages de commit clairs
- [ ] Documentation mise à jour si nécessaire
- [ ] Code commenté si complexe

## 📚 Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Alpine.js](https://alpinejs.dev/)
- [SQLModel](https://sqlmodel.tiangolo.com/)

## 🙏 Merci !

Chaque contribution, petite ou grande, est appréciée !
