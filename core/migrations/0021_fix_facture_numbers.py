# Generated manually to fix facture numbers

from django.db import migrations
import uuid
from datetime import datetime

def fix_facture_numbers(apps, schema_editor):
    """Corriger les numéros de facture existants pour éviter les doublons"""
    Facture = apps.get_model('core', 'Facture')
    
    # Récupérer toutes les factures
    factures = Facture.objects.all()
    
    # Créer un dictionnaire pour suivre les numéros existants par boutique
    numeros_par_boutique = {}
    
    for facture in factures:
        boutique_id = facture.boutique.id if facture.boutique else 1
        
        if boutique_id not in numeros_par_boutique:
            numeros_par_boutique[boutique_id] = set()
        
        # Si le numéro est vide ou null, générer un nouveau
        if not facture.numero or facture.numero == '':
            # Générer un numéro au format YYYY-MM-BOUTIQUE-NNNN
            now = datetime.now()
            boutique_nom = facture.boutique.nom[:6].upper() if facture.boutique else 'BTQ001'
            numero_base = f"{now.year}-{now.month:02d}-{boutique_nom}"
            
            # Trouver le prochain numéro disponible
            compteur = 1
            while f"{numero_base}-{compteur:04d}" in numeros_par_boutique[boutique_id]:
                compteur += 1
            
            facture.numero = f"{numero_base}-{compteur:04d}"
            facture.save()
        
        # Ajouter le numéro à notre set de suivi
        numeros_par_boutique[boutique_id].add(facture.numero)

def reverse_fix_facture_numbers(apps, schema_editor):
    """Pas de rollback nécessaire"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_commandeclient_options_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_facture_numbers, reverse_fix_facture_numbers),
    ]



