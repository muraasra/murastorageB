from rest_framework import serializers
from .models import SubscriptionPlan, EntrepriseSubscription, UsageTracking

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les plans d'abonnement"""
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class EntrepriseSubscriptionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les abonnements d'entreprise"""
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = EntrepriseSubscription
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'start_date')
    
    def validate_plan_id(self, value):
        """Valider que le plan existe"""
        try:
            SubscriptionPlan.objects.get(id=value, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Plan d'abonnement invalide")
        return value

class UsageTrackingSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le suivi d'utilisation"""
    class Meta:
        model = UsageTracking
        fields = '__all__'
        read_only_fields = ('last_updated',)

class SubscriptionLimitsSerializer(serializers.Serializer):
    """Sérialiseur pour les limites d'abonnement"""
    plan_name = serializers.CharField()
    display_name = serializers.CharField()
    max_entreprises = serializers.IntegerField()
    max_boutiques = serializers.IntegerField()
    max_users = serializers.IntegerField()
    max_produits = serializers.IntegerField(allow_null=True)
    max_factures_per_month = serializers.IntegerField(allow_null=True)
    allow_export_csv = serializers.BooleanField()
    allow_export_excel = serializers.BooleanField()
    allow_import_csv = serializers.BooleanField()
    allow_api_access = serializers.BooleanField()
    allow_multiple_entreprises = serializers.BooleanField()
    allow_advanced_analytics = serializers.BooleanField()
    allow_custom_branding = serializers.BooleanField()
    support_level = serializers.CharField()
    price_monthly = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = serializers.DecimalField(max_digits=10, decimal_places=2)

class CurrentUsageSerializer(serializers.Serializer):
    """Sérialiseur pour l'utilisation actuelle"""
    factures_count = serializers.IntegerField()
    produits_count = serializers.IntegerField()
    users_count = serializers.IntegerField()
    boutiques_count = serializers.IntegerField()
    factures_limit = serializers.IntegerField(allow_null=True)
    produits_limit = serializers.IntegerField(allow_null=True)
    users_limit = serializers.IntegerField()
    boutiques_limit = serializers.IntegerField()
    is_factures_limit_reached = serializers.BooleanField()
    is_produits_limit_reached = serializers.BooleanField()
    is_users_limit_reached = serializers.BooleanField()
    is_boutiques_limit_reached = serializers.BooleanField()






































