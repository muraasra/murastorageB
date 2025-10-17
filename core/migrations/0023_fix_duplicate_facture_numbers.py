# Generated manually to fix duplicate facture numbers

from django.db import migrations
import uuid
from datetime import datetime

def fix_duplicate_facture_numbers(apps, schema_editor):
    """Corriger les numéros de facture en doublon"""
    Facture = apps.get_model('core', 'Facture')
    
    # Récupérer toutes les factures
    factures = Facture.objects.all().order_by('id')
    
    # Créer un dictionnaire pour suivre les numéros existants
    numeros_existants = set()
    
    for facture in factures:
        # Si le numéro existe déjà ou est vide, générer un nouveau
        if not facture.numero or facture.numero == '' or facture.numero in numeros_existants:
            # Générer un numéro au format YYYY-MM-BOUTIQUE-NNNN
            now = datetime.now()
            boutique_nom = facture.boutique.nom[:6].upper() if facture.boutique else 'BTQ001'
            numero_base = f"{now.year}-{now.month:02d}-{boutique_nom}"
            
            # Trouver le prochain numéro disponible
            compteur = 1
            nouveau_numero = f"{numero_base}-{compteur:04d}"
            
            while nouveau_numero in numeros_existants:
                compteur += 1
                nouveau_numero = f"{numero_base}-{compteur:04d}"
            
            facture.numero = nouveau_numero
            facture.save()
            print(f"Facture ID {facture.id}: {facture.numero}")
        
        # Ajouter le numéro à notre set de suivi
        numeros_existants.add(facture.numero)

def reverse_fix_duplicate_facture_numbers(apps, schema_editor):
    """Pas de rollback nécessaire"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_merge_0020_sequencefacture_0021_fix_facture_numbers'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_facture_numbers, reverse_fix_duplicate_facture_numbers),
    ]



