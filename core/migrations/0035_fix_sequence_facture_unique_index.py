# Generated manually to fix unique index issue on SequenceFacture
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_fix_sequence_facture_foreignkey'),
    ]

    operations = [
        # Supprimer l'ancien index unique sur boutique_id seul (s'il existe)
        migrations.RunSQL(
            # Supprimer l'index unique sur boutique_id s'il existe
            sql="ALTER TABLE core_sequencefacture DROP INDEX IF EXISTS core_sequencefacture_boutique_id;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # S'assurer que l'index unique composite (boutique, annee, mois) existe
        migrations.RunSQL(
            # Créer l'index unique composite si nécessaire
            sql="""
            CREATE UNIQUE INDEX IF NOT EXISTS core_sequencefacture_boutique_annee_mois_uniq 
            ON core_sequencefacture(boutique_id, annee, mois);
            """,
            reverse_sql="DROP INDEX IF EXISTS core_sequencefacture_boutique_annee_mois_uniq ON core_sequencefacture;",
        ),
    ]

