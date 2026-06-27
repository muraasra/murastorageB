"""
Signaux Django pour la logique métier automatique.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum


@receiver([post_save, post_delete], sender='core.Versement')
def recalculer_reste_facture(sender, instance, **kwargs):
    """
    Recalcule automatiquement Facture.reste et Facture.status
    après chaque ajout ou suppression d'un versement.
    """
    facture = instance.facture
    total_verse = facture.versements.aggregate(total=Sum('montant'))['total'] or 0
    nouveau_reste = max(0, facture.total - total_verse)

    if nouveau_reste <= 0:
        nouveau_status = 'Payé'
    elif total_verse > 0:
        nouveau_status = 'Partiellement payé'
    else:
        nouveau_status = 'En attente'

    # Mise à jour sans déclencher d'autres signaux (update_fields)
    type(facture).objects.filter(pk=facture.pk).update(
        reste=nouveau_reste,
        status=nouveau_status,
    )
