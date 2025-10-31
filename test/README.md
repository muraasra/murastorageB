# Dossier de Tests - StoRage Management System

Ce dossier contient tous les scripts de test et de debug pour le système StoRage.

## 📁 Organisation des fichiers

### 🧪 Tests d'API
- **`test_all_apis.py`** - Test général de toutes les APIs
- **`test_final_complete.py`** - Test final complet avec statistiques
- **`test_with_auth.py`** - Test avec authentification

### 🔐 Tests d'authentification
- **`test_jwt_auth.py`** - Test de l'authentification JWT
- **`test_jwt_complete.py`** - Test complet JWT avec toutes les informations
- **`test_jwt_curl.py`** - Test JWT avec curl
- **`test_simple_jwt.py`** - Test simple JWT
- **`test_permissions_debug.py`** - Debug des permissions

### 📝 Tests d'inscription
- **`test_inscription_api.py`** - Test de l'API d'inscription
- **`test_inscription_debug.py`** - Debug spécifique de l'inscription

### 🔧 Scripts de debug
- **`debug_jwt_error.py`** - Debug des erreurs JWT
- **`debug_user_status.py`** - Debug de l'état des utilisateurs

### 🛠️ Scripts de correction
- **`fix_existing_users.py`** - Correction des utilisateurs existants
- **`manual_fix_users.py`** - Association manuelle utilisateur-entreprise

## 🚀 Comment utiliser

### Prérequis
1. Assurez-vous que le serveur Django est démarré :
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

2. Exécutez les tests depuis le dossier Backend :
   ```bash
   python test/test_all_apis.py
   python test/test_jwt_complete.py
   ```

### Tests recommandés

1. **Test complet du système** :
   ```bash
   python test/test_final_complete.py
   ```

2. **Test JWT avec informations complètes** :
   ```bash
   python test/test_jwt_complete.py
   ```

3. **Debug des utilisateurs** :
   ```bash
   python test/debug_user_status.py
   ```

## 📊 Résultats des tests

Les tests génèrent des fichiers de résultats :
- `test_results.json` - Résultats des tests généraux
- `test_final_results.json` - Résultats des tests finaux

## 🔍 Debug

En cas de problème, utilisez les scripts de debug :
- `debug_user_status.py` - Vérifier l'état des utilisateurs
- `debug_jwt_error.py` - Debug des erreurs JWT
- `test_permissions_debug.py` - Debug des permissions

## 📝 Notes

- Tous les tests utilisent des données de test avec des timestamps pour éviter les conflits
- Les tests créent des entreprises et utilisateurs de test
- Les données de test sont automatiquement nettoyées ou peuvent être supprimées manuellement
























































