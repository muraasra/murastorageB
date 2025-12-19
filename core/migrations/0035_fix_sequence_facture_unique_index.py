# Generated manually to fix unique index issue on SequenceFacture
from django.db import migrations, connection


def fix_sequencefacture_indexes(apps, schema_editor):
    """
    Corrige les index de la table core_sequencefacture pour MySQL :
    - Supprime tout index UNIQUE sur boutique_id seul
    - Ajoute un index UNIQUE composite (boutique_id, annee, mois) s'il n'existe pas
    """
    table_name = 'core_sequencefacture'

    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, table_name)

        # 1) Supprimer les index uniques sur boutique_id seul
        for name, info in constraints.items():
            cols = info.get('columns') or []
            is_unique = info.get('unique', False)
            if is_unique and cols == ['boutique_id']:
                schema_editor.execute(f"ALTER TABLE {table_name} DROP INDEX {name}")

        # Recharger les contraintes après suppression
        constraints = connection.introspection.get_constraints(cursor, table_name)

        # 2) Vérifier si l'index unique composite (boutique_id, annee, mois) existe déjà
        has_composite_unique = False
        for name, info in constraints.items():
            cols = info.get('columns') or []
            is_unique = info.get('unique', False)
            if is_unique and cols == ['boutique_id', 'annee', 'mois']:
                has_composite_unique = True
                break

        # 3) Créer l'index unique composite si nécessaire
        if not has_composite_unique:
            schema_editor.execute(
                "CREATE UNIQUE INDEX core_sequencefacture_boutique_annee_mois_uniq "
                "ON core_sequencefacture (boutique_id, annee, mois)"
            )


def noop(apps, schema_editor):
    # Pas de rollback spécifique
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_fix_sequence_facture_foreignkey'),
    ]

    operations = [
        migrations.RunPython(fix_sequencefacture_indexes, noop),
    ]

