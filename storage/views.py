from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Ajoute des données personnalisées à la réponse
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email  # optionnel
        data['role'] = self.user.role  # Ajout du rôle de l'utilisateur
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]