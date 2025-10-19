# create_test_mouvements.py
import os
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storage.settings')
django.setup()

from core.models import User, Boutique, Produit, Stock, MouvementStock

def create_test_mouvements():
    print("🔍 CRÉATION DE MOUVEMENTS DE STOCK DE TEST")
    print("=" * 60)
    
    # Récupérer un utilisateur superadmin
    user = User.objects.filter(is_active=True, role='superadmin').first()
    if not user:
        print("❌ Aucun utilisateur superadmin trouvé")
        return
    
    print(f"👤 Utilisateur: {user.username}")
    print(f"🏢 Entreprise: {user.entreprise.nom}")
    
    # Récupérer une boutique
    boutique = Boutique.objects.filter(entreprise=user.entreprise).first()
    if not boutique:
        print("❌ Aucune boutique trouvée")
        return
    
    print(f"🏪 Boutique: {boutique.nom}")
    
    # Récupérer des produits
    produits = Produit.objects.filter(entreprise=user.entreprise)[:3]
    if not produits:
        print("❌ Aucun produit trouvé")
        return
    
    print(f"📦 Produits trouvés: {len(produits)}")
    
    # Créer des mouvements de stock de test
    mouvements_crees = 0
    
    for i, produit in enumerate(produits):
        # Créer un mouvement d'entrée
        mouvement_entree = MouvementStock.objects.create(
            produit=produit,
            entrepot=boutique,
            type_mouvement='entree',
            quantite=10 + i * 5,  # 10, 15, 20
            quantite_avant=0,
            quantite_apres=10 + i * 5,
            reference_document=f'ENTREE-{datetime.now().strftime("%Y%m%d")}-{i+1:03d}',
            motif=f'Entrée de stock de test pour {produit.nom}',
            utilisateur=user,
            created_at=datetime.now() - timedelta(days=i+1)
        )
        mouvements_crees += 1
        print(f"✅ Mouvement entrée créé: {produit.nom} - {mouvement_entree.quantite} unités")
        
        # Créer un mouvement de sortie
        mouvement_sortie = MouvementStock.objects.create(
            produit=produit,
            entrepot=boutique,
            type_mouvement='sortie',
            quantite=2 + i,  # 2, 3, 4
            quantite_avant=10 + i * 5,
            quantite_apres=8 + i * 4,
            reference_document=f'SORTIE-{datetime.now().strftime("%Y%m%d")}-{i+1:03d}',
            motif=f'Sortie de stock de test pour {produit.nom}',
            utilisateur=user,
            created_at=datetime.now() - timedelta(hours=i*6)
        )
        mouvements_crees += 1
        print(f"✅ Mouvement sortie créé: {produit.nom} - {mouvement_sortie.quantite} unités")
    
    # Créer un mouvement de transfert
    if len(produits) > 1:
        mouvement_transfert = MouvementStock.objects.create(
            produit=produits[0],
            entrepot=boutique,
            type_mouvement='transfert',
            quantite=5,
            quantite_avant=8,
            quantite_apres=3,
            reference_document=f'TRANSFERT-{datetime.now().strftime("%Y%m%d")}-001',
            motif=f'Transfert de stock de test pour {produits[0].nom}',
            utilisateur=user,
            created_at=datetime.now() - timedelta(hours=2)
        )
        mouvements_crees += 1
        print(f"✅ Mouvement transfert créé: {produits[0].nom} - {mouvement_transfert.quantite} unités")
    
    print(f"\n🎉 {mouvements_crees} mouvements de stock créés avec succès!")
    
    # Vérifier le total
    total_mouvements = MouvementStock.objects.count()
    print(f"📊 Total des mouvements en base: {total_mouvements}")
    
    # Lister les mouvements récents
    mouvements_recents = MouvementStock.objects.all().order_by('-created_at')[:5]
    print(f"\n📋 Derniers mouvements:")
    for mouvement in mouvements_recents:
        print(f"   - {mouvement.produit.nom} | {mouvement.type_mouvement} | {mouvement.quantite} | {mouvement.created_at.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    create_test_mouvements()






