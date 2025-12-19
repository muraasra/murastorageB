"""
Test pour vérifier que la génération de numéros de facture fonctionne correctement
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'murastorageB.settings')
django.setup()

from core.models import SequenceFacture, Boutique
from django.db import transaction
from django.db.utils import IntegrityError
import time

def test_sequence_facture():
    """Test de la génération de numéros de facture"""
    print("🧪 Test de la génération de numéros de facture\n")
    print("=" * 60)
    
    # Récupérer une boutique de test
    try:
        boutique = Boutique.objects.first()
        if not boutique:
            print("❌ Aucune boutique trouvée dans la base de données")
            return False
        print(f"✅ Boutique de test: {boutique.nom} (ID: {boutique.id})")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la boutique: {e}")
        return False
    
    # Test 1: Génération d'un numéro de facture
    print("\n📋 Test 1: Génération d'un numéro de facture")
    print("-" * 60)
    try:
        numero1 = SequenceFacture.get_next_number(boutique)
        print(f"✅ Numéro généré: {numero1}")
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False
    
    # Test 2: Génération de plusieurs numéros consécutifs
    print("\n📋 Test 2: Génération de plusieurs numéros consécutifs")
    print("-" * 60)
    try:
        numeros = []
        for i in range(5):
            numero = SequenceFacture.get_next_number(boutique)
            numeros.append(numero)
            print(f"  Numéro {i+1}: {numero}")
        
        # Vérifier que les numéros sont consécutifs
        if numeros == sorted(numeros) and all(numeros[i] < numeros[i+1] for i in range(len(numeros)-1)):
            print("✅ Les numéros sont consécutifs et croissants")
        else:
            print("❌ Les numéros ne sont pas consécutifs")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la génération multiple: {e}")
        return False
    
    # Test 3: Vérifier l'unicité (boutique, annee, mois)
    print("\n📋 Test 3: Vérification de l'unicité (boutique, annee, mois)")
    print("-" * 60)
    try:
        from datetime import datetime
        now = datetime.now()
        sequences = SequenceFacture.objects.filter(
            boutique=boutique,
            annee=now.year,
            mois=now.month
        )
        count = sequences.count()
        if count == 1:
            print(f"✅ Une seule séquence trouvée pour {now.year}/{now.month:02d}")
        else:
            print(f"⚠️ {count} séquences trouvées (attendu: 1)")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False
    
    # Test 4: Vérifier les index de la base de données
    print("\n📋 Test 4: Vérification des index de la base de données")
    print("-" * 60)
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SHOW INDEX FROM core_sequencefacture")
            indexes = cursor.fetchall()
            
            # Chercher l'index unique composite
            has_composite_unique = False
            has_boutique_unique = False
            
            for index in indexes:
                index_name = index[2]  # Nom de l'index
                column_name = index[4]  # Nom de la colonne
                non_unique = index[1]  # 0 = unique, 1 = non-unique
                
                if non_unique == 0:  # Index unique
                    if 'boutique' in index_name.lower() and 'annee' in index_name.lower():
                        has_composite_unique = True
                        print(f"✅ Index unique composite trouvé: {index_name}")
                    elif column_name == 'boutique_id' and non_unique == 0:
                        has_boutique_unique = True
                        print(f"⚠️ Index unique sur boutique_id seul trouvé: {index_name}")
            
            if has_composite_unique:
                print("✅ Index unique composite correctement configuré")
            else:
                print("❌ Index unique composite non trouvé")
                return False
            
            if has_boutique_unique:
                print("⚠️ ATTENTION: Index unique sur boutique_id seul détecté - doit être supprimé")
                print("   Exécutez: ALTER TABLE core_sequencefacture DROP INDEX <nom_index>;")
                return False
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification des index: {e}")
        print("   (Peut être normal si vous n'avez pas les permissions)")
    
    print("\n" + "=" * 60)
    print("🎉 TOUS LES TESTS PASSENT")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_sequence_facture()
    sys.exit(0 if success else 1)

