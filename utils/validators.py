import re
from rest_framework.exceptions import ValidationError

# Validation du numéro de téléphone
def validate_phone(value):
    """Valide le numéro de téléphone."""      
    if not isinstance(value, str):
        raise ValidationError("Le numéro de téléphone doit être un champ texte.")
    if not value.isdigit():
        raise ValidationError("Le numéro de téléphone ne doit contenir que des chiffres.")
    return value

# Validation de l'email
def validate_email(value):
    """Valide l'adresse email."""  
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise ValidationError("Adresse email invalide.")
    return value
