# 🔧 Guide de Correction - Erreur SequenceFacture

## 📋 Problème Identifié

**Erreur:** `Duplicate entry '1' for key 'core_sequencefacture.boutique_id'`

**Cause:** La base de données MySQL a un index unique sur `boutique_id` seul, alors que le modèle Django utilise `unique_together = [['boutique', 'annee', 'mois']]`. Cela crée un conflit lors de la création de nouvelles séquences pour le même entrepôt mais des mois/années différents.

## ✅ Solutions Implémentées

### 1. Migration Django (Recommandé)

Une nouvelle migration `0035_fix_sequence_facture_unique_index.py` a été créée pour :
- Supprimer l'ancien index unique sur `boutique_id` seul
- Créer l'index unique composite `(boutique_id, annee, mois)`

**Pour appliquer:**
```bash
cd /home/murastorage/murastorageB
python manage.py migrate core
```

### 2. Script SQL Direct (Alternative)

Si la migration ne fonctionne pas, exécutez directement le script SQL:
```bash
mysql -u murastorage -p murastorage$default < fix_sequence_facture_index.sql
```

Ou via la console MySQL de PythonAnywhere:
```sql
-- Vérifier les index existants
SHOW INDEX FROM core_sequencefacture;

-- Supprimer l'ancien index unique sur boutique_id
ALTER TABLE core_sequencefacture DROP INDEX IF EXISTS core_sequencefacture_boutique_id;

-- Créer l'index unique composite
CREATE UNIQUE INDEX IF NOT EXISTS core_sequencefacture_boutique_annee_mois_uniq 
ON core_sequencefacture(boutique_id, annee, mois);
```

### 3. Améliorations du Code

#### Backend (`core/models.py`)
- ✅ Amélioration de `get_next_number()` avec meilleure gestion des erreurs
- ✅ Retry automatique en cas de race condition (5 tentatives)
- ✅ Utilisation de `select_for_update(nowait=True)` pour éviter les deadlocks
- ✅ Messages d'erreur plus explicites

#### Frontend (`pages/facturation.vue`)
- ✅ Détection spécifique de l'erreur de transaction
- ✅ Message d'erreur plus clair pour l'utilisateur
- ✅ Logging amélioré pour le débogage

## 🧪 Test de la Correction

### Test Automatique
```bash
cd /home/murastorage/murastorageB
python test_sequence_facture.py
```

### Test Manuel
1. Créer une facture depuis l'interface web
2. Vérifier qu'elle est créée avec succès
3. Vérifier que le numéro de facture est généré correctement
4. Créer plusieurs factures consécutives pour vérifier l'incrémentation

## 📝 Vérification Post-Correction

### Vérifier les Index
```sql
SHOW INDEX FROM core_sequencefacture;
```

Vous devriez voir:
- ✅ Un index unique sur `(boutique_id, annee, mois)`
- ❌ PAS d'index unique sur `boutique_id` seul

### Vérifier les Données
```sql
SELECT boutique_id, annee, mois, COUNT(*) as count
FROM core_sequencefacture
GROUP BY boutique_id, annee, mois
HAVING count > 1;
```

Cette requête ne devrait retourner aucun résultat (pas de doublons).

## 🚨 En Cas de Problème

### Si la migration échoue
1. Vérifiez les permissions MySQL
2. Vérifiez qu'il n'y a pas de transactions en cours
3. Exécutez le script SQL directement

### Si des doublons existent déjà
1. Identifiez les doublons:
```sql
SELECT boutique_id, annee, mois, COUNT(*) as count
FROM core_sequencefacture
GROUP BY boutique_id, annee, mois
HAVING count > 1;
```

2. Supprimez les doublons en gardant le plus récent:
```sql
DELETE s1 FROM core_sequencefacture s1
INNER JOIN core_sequencefacture s2 
WHERE s1.id < s2.id 
AND s1.boutique_id = s2.boutique_id
AND s1.annee = s2.annee
AND s1.mois = s2.mois;
```

## ✅ Checklist de Déploiement

- [ ] Appliquer la migration ou exécuter le script SQL
- [ ] Redémarrer l'application uWSGI
- [ ] Tester la création d'une facture
- [ ] Vérifier les logs pour confirmer l'absence d'erreurs
- [ ] Vérifier que les numéros de facture sont générés correctement

## 📞 Support

Si le problème persiste après ces corrections, vérifiez:
1. Les logs Django pour les erreurs détaillées
2. Les logs MySQL pour les erreurs de contraintes
3. La configuration de la base de données

