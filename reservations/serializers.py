from rest_framework import serializers
from .models import Reservation, Creneau
from utils.validators import validate_phone, validate_email

class ReservationSerializer(serializers.ModelSerializer):
    # Application du validateur personnalisé pour le téléphone
    telephone = serializers.CharField(validators=[validate_phone])
    
    # Application du validateur personnalisé pour l'email
    email = serializers.EmailField(required = True, validators=[validate_email])

    class Meta:
        model = Reservation
        fields = '__all__'

    def validate_email(self, value):
        """Valide que l'email est bien fourni."""
        if not value:
            raise serializers.ValidationError("L'email est obligatoire pour effectuer une réservation.")
        return value


class CreneauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creneau
        fields = '__all__'