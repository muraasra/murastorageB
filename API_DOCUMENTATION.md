# Documentation API - Inscription Entreprise

## Endpoint d'inscription

**POST** `/api/inscription/inscription/`

### Description
Crée une nouvelle entreprise avec un utilisateur SuperAdmin. Envoie automatiquement un email de vérification à l'utilisateur.

### Structure des données attendues

```json
{
  "user": {
    "nom": "string (requis, max 150 caractères)",
    "prenom": "string (requis, max 150 caractères)", 
    "email": "string (requis, format email valide)",
    "telephone": "string (requis, max 20 caractères)",
    "mot_de_passe": "string (requis, minimum 8 caractères)",
    "role": "string (optionnel, défaut: 'superadmin')"
  },
  "nom": "string (requis, max 200 caractères)",
  "description": "string (optionnel)",
  "secteur_activite": "string (requis, max 100 caractères)",
  "adresse": "string (requis)",
  "ville": "string (requis, max 100 caractères)",
  "code_postal": "string (optionnel, max 20 caractères)",
  "pays": "string (optionnel, défaut: 'Cameroun')",
  "telephone": "string (optionnel, max 20 caractères)",
  "email": "string (requis, format email valide)",
  "site_web": "string (optionnel, format URL valide)",
  "numero_fiscal": "string (optionnel, max 50 caractères)",
  "nombre_employes": "integer (optionnel, défaut: 0, minimum: 0)",
  "annee_creation": "integer (requis, entre 1900 et année actuelle)",
  "pack_type": "string (requis, choix: 'basique', 'professionnel', 'entreprise')",
  "pack_prix": "float (optionnel, défaut: 0)",
  "pack_duree": "string (optionnel, défaut: 'mensuel')",
  "is_active": "boolean (optionnel, défaut: true)"
}
```

### Exemple de requête

```json
VA 
```

### Réponse de succès (201 Created)

```json
{
  "success": true,
  "message": "Entreprise créée avec succès. Un email de vérification a été envoyé.",
  "entreprise": {
    "id_entreprise": "ABC1234567",
    "nom": "Entreprise Example",
    "description": "Une entreprise de gestion de stock",
    "secteur_activite": "Technologie et Informatique",
    "adresse": "123 Rue de la Paix",
    "ville": "Douala",
    "code_postal": "00000",
    "pays": "Cameroun",
    "telephone": "+237 2XX XX XX XX",
    "email": "contact@entreprise-example.com",
    "site_web": "https://www.entreprise-example.com",
    "numero_fiscal": "123456789",
    "nombre_employes": 5,
    "annee_creation": 2020,
    "pack_type": "professionnel",
    "pack_prix": 49.0,
    "pack_duree": "mensuel",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### Réponse d'erreur (400 Bad Request)

```json
{
  "success": false,
  "message": "Erreur lors de la création: [détails de l'erreur]"
}
```

### Actions automatiques

Lors de la création réussie d'une entreprise, le système :

1. **Crée l'utilisateur SuperAdmin** avec les données fournies
2. **Crée un entrepôt par défaut** nommé "Entrepôt Principal - [Nom de l'entreprise]"
3. **Assigne l'entrepôt** à l'utilisateur SuperAdmin
4. **Envoie un email de vérification** avec un code à 6 chiffres
5. **Retourne les données** de l'entreprise créée

### Validation des données

- **Email utilisateur** : Doit être unique et valide
- **Mot de passe** : Minimum 8 caractères
- **Année de création** : Entre 1900 et l'année actuelle
- **Nombre d'employés** : Ne peut pas être négatif
- **Pack type** : Doit être l'un des choix autorisés
- **Site web** : Doit être une URL valide si fourni

### Codes d'erreur courants

- **400** : Données invalides ou manquantes
- **500** : Erreur serveur interne
























































