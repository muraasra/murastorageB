# Guide de Configuration des Notifications Automatiques en Production

## 📋 Vue d'ensemble

Le système d'envoi d'emails automatiques permet de :
- ✅ **Alertes de stock faible** : Notifier quand un produit approche du stock minimum
- ✅ **Alertes de rupture de stock** : Notifier quand un produit est en rupture (quantité = 0)
- ✅ **Résumés quotidiens** : Envoyer un récapitulatif des stocks chaque jour
- ✅ **Alertes d'abonnement** : Notifier les limites atteintes, périodes d'essai, expirations

## 🔧 Configuration Email en Production

### 1. Vérifier les paramètres dans `settings.py`

Assurez-vous que la configuration email est correcte :

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'wilfriedtayou6@gmail.com'
EMAIL_HOST_PASSWORD = 'unma mqpz bvsx dpmr'  # Mot de passe d'application Gmail
DEFAULT_FROM_EMAIL = 'wilfriedtayou6@gmail.com'
FRONTEND_URL = 'https://murastorage.netlify.app'  # URL du frontend
```

### 2. Sécurité : Utiliser des variables d'environnement (Recommandé)

Pour la production, utilisez des variables d'environnement :

```python
import os

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'wilfriedtayou6@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'unma mqpz bvsx dpmr')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
```

## 📅 Configuration des Tâches Planifiées

### Option 1 : PythonAnywhere (Recommandé pour ce projet)

PythonAnywhere permet de planifier des tâches via l'interface web :

1. **Accéder aux Scheduled Tasks** :
   - Connectez-vous à PythonAnywhere
   - Allez dans l'onglet "Tasks"
   - Cliquez sur "Create a new task"

2. **Configurer la tâche quotidienne** :
   ```
   Command: python3.10 /home/murastorage/walner-durel/Backend/manage.py send_notifications
   Hour: 8 (ou l'heure souhaitée)
   Minute: 0
   ```

3. **Créer une tâche pour les alertes urgentes** (toutes les 2 heures) :
   ```
   Command: python3.10 /home/murastorage/walner-durel/Backend/manage.py send_notifications --stock
   Hour: */2 (toutes les 2 heures)
   ```

### Option 2 : Cron Job (Serveur Linux/VPS)

1. **Ouvrir le crontab** :
   ```bash
   crontab -e
   ```

2. **Ajouter les tâches** :
   ```cron
   # Notifications complètes tous les jours à 8h00
   0 8 * * * cd /chemin/vers/Backend && /usr/bin/python3 manage.py send_notifications >> /var/log/notifications.log 2>&1

   # Alertes de stock urgentes toutes les 2 heures
   0 */2 * * * cd /chemin/vers/Backend && /usr/bin/python3 manage.py send_notifications --stock >> /var/log/notifications_stock.log 2>&1

   # Résumés quotidiens à 18h00
   0 18 * * * cd /chemin/vers/Backend && /usr/bin/python3 manage.py send_notifications --summary >> /var/log/notifications_summary.log 2>&1
   ```

### Option 3 : Windows Task Scheduler (Développement local)

1. Ouvrir "Planificateur de tâches"
2. Créer une tâche de base
3. **Déclencheur** : Quotidien à 8h00
4. **Action** : Exécuter un programme
   - Programme : `C:\Python\python.exe`
   - Arguments : `E:\walner-durel\Backend\manage.py send_notifications`
   - Démarrer dans : `E:\walner-durel\Backend`

## 🧪 Tester les Notifications

### Test manuel depuis le terminal

```bash
# Toutes les notifications
python manage.py send_notifications

# Seulement les alertes de stock
python manage.py send_notifications --stock

# Seulement les alertes d'abonnement
python manage.py send_notifications --subscription

# Seulement les résumés quotidiens
python manage.py send_notifications --summary
```

### Test depuis Python

```python
python manage.py shell

from core.management.commands.send_notifications import Command
cmd = Command()
cmd.handle()
```

## 📊 Fréquence Recommandée

| Type de notification | Fréquence | Urgence |
|---------------------|-----------|---------|
| **Alertes de rupture de stock** | Toutes les 2-4 heures | 🔴 URGENT |
| **Alertes de stock faible** | 1-2 fois par jour | 🟡 IMPORTANT |
| **Alertes d'abonnement (limites)** | 1 fois par jour | 🟡 IMPORTANT |
| **Alertes d'expiration** | 1 fois par jour | 🟡 IMPORTANT |
| **Résumés quotidiens** | 1 fois par jour (18h) | 🟢 INFO |

## ⚠️ Problèmes Courants

### 1. Les emails ne sont pas envoyés

**Vérifications** :
- ✅ Configuration email correcte dans `settings.py`
- ✅ Mot de passe d'application Gmail valide (pas le mot de passe du compte)
- ✅ Pas de blocage de sécurité Gmail
- ✅ `FRONTEND_URL` correctement configuré

**Solution** : Activer "Accès moins sécurisé" ou utiliser un "Mot de passe d'application" Gmail

### 2. Les tâches planifiées ne s'exécutent pas

**Vérifications** :
- ✅ Chemin Python correct
- ✅ Permissions d'exécution
- ✅ Fichiers de logs pour voir les erreurs

**Solution** : Vérifier les logs (`/var/log/notifications.log`)

### 3. Emails envoyés mais non reçus

**Vérifications** :
- ✅ Vérifier les spams
- ✅ Email destinataire valide
- ✅ Limite d'envoi Gmail non atteinte (500/jour pour compte gratuit)

## 📝 Logs et Monitoring

Les notifications enregistrent automatiquement :
- ✅ Nombre d'alertes envoyées
- ✅ Erreurs rencontrées
- ✅ Heure d'exécution

Pour activer les logs détaillés, rediriger la sortie :

```bash
python manage.py send_notifications >> notifications.log 2>&1
```

## 🔐 Sécurité Production

1. **Variables d'environnement** : Ne jamais commiter les mots de passe
2. **Gmail App Password** : Utiliser un mot de passe d'application, pas le mot de passe principal
3. **Rate Limiting** : Respecter les limites Gmail (500 emails/jour)
4. **Monitoring** : Surveiller les échecs d'envoi

## ✅ Checklist Production

- [ ] Configuration email testée et fonctionnelle
- [ ] Tâches planifiées configurées (cron/PythonAnywhere)
- [ ] Test d'envoi réussi pour chaque type de notification
- [ ] Variables d'environnement configurées (si utilisé)
- [ ] Logs configurés et monitorés
- [ ] `FRONTEND_URL` pointant vers le domaine de production
- [ ] Gmail App Password configuré

## 📞 Support

En cas de problème, vérifier :
1. Les logs Django (`python manage.py runserver`)
2. Les logs de cron (si utilisé)
3. La console PythonAnywhere (si utilisé)
4. Les emails de bounce/erreur Gmail

