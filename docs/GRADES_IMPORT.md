# 📝 Guide d'Import des Notes

## Vue d'ensemble

AutoDesk Kiwi permet maintenant d'importer vos notes manuellement pour les afficher dans la section Hyperplanning.

## Comment ça marche ?

### 1️⃣ Préparer vos notes

Vos notes doivent être au format JSON (un tableau d'objets). Chaque note contient :
- `subject` : Le nom de la matière
- `date` : La date de la note (format libre, ex: "13 déc.")
- `value` : La valeur de la note (sur 20)

**Exemple :**
```json
[
  {"subject": "Admin & séc infra réseau", "date": "18 déc.", "value": 18.39},
  {"subject": "Anglais", "date": "13 déc.", "value": 15.50},
  {"subject": "Supervision des infras", "date": "12 déc.", "value": 10.00}
]
```

### 2️⃣ Importer vos notes

1. **Ouvrez AutoDesk Kiwi** dans votre navigateur
2. **Allez dans l'onglet "🎓 Hyperplanning"**
3. Dans la section "📝 Dernières notes", **cliquez sur "➕ Importer"**
4. **Collez votre JSON** dans la zone de texte
5. **Cliquez sur "✅ Importer"**

### 3️⃣ Résultat

- Vos notes apparaissent immédiatement
- Les notes sont **sauvegardées en base de données** SQLite
- Elles persistent même après redémarrage

## Fichier d'exemple

Un fichier d'exemple est disponible : [`docs/example_grades.json`](example_grades.json)

Vous pouvez copier-coller son contenu directement dans l'interface d'import.

## Supprimer toutes les notes

Si vous voulez réimporter vos notes (par exemple, nouvelles notes disponibles) :

1. Cliquez sur **"🗑️ Tout supprimer"**
2. Confirmez la suppression
3. Importez vos nouvelles notes

## API Endpoints

Pour les développeurs, voici les endpoints disponibles :

### GET `/hyperplanning/grades`
Récupère toutes les notes (triées par date de création décroissante).

**Réponse :**
```json
[
  {
    "id": 1,
    "subject": "Anglais",
    "date": "13 déc.",
    "value": 15.5,
    "created_at": "2026-01-23T10:30:00Z"
  }
]
```

### POST `/hyperplanning/grades/import`
Importe des notes (remplace toutes les notes existantes).

**Body :**
```json
{
  "grades": [
    {"subject": "Matière", "date": "13 déc.", "value": 15.5}
  ]
}
```

**Réponse :**
```json
{
  "message": "5 note(s) importée(s) avec succès",
  "count": 5,
  "grades": [...]
}
```

### DELETE `/hyperplanning/grades/clear`
Supprime toutes les notes.

**Réponse :**
```json
{
  "message": "10 note(s) supprimée(s)",
  "count": 10
}
```

## Conseils

### 📋 Comment récupérer vos notes depuis Hyperplanning ?

Puisque l'API Hyperplanning est chiffrée, voici comment procéder manuellement :

1. **Copiez vos notes** depuis l'interface web Hyperplanning
2. **Formatez-les en JSON** (vous pouvez utiliser un outil comme Excel/Google Sheets)
3. **Importez-les** dans AutoDesk Kiwi

### 🔄 Fréquence d'import

- **1 fois par semaine** : pour avoir les notes à jour
- **Après chaque évaluation** : pour être toujours synchronisé

## Validation

Les notes sont validées avant l'import :
- `subject` : obligatoire, max 200 caractères
- `date` : obligatoire, max 50 caractères
- `value` : obligatoire, doit être entre 0 et 20

Si une note ne passe pas la validation, l'import échouera avec un message d'erreur.

## Problèmes courants

### ❌ "Format JSON invalide"
→ Vérifiez la syntaxe de votre JSON (virgules, guillemets, crochets)

### ❌ "Le JSON doit être un tableau"
→ Votre JSON doit commencer par `[` et finir par `]`

### ❌ "value must be between 0 and 20"
→ Les notes doivent être sur 20 (utilisez des décimales si nécessaire, ex: 15.5)

## Support

Pour toute question, ouvrez une issue sur le projet GitHub.
