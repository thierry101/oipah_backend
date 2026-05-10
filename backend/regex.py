import re

import base64
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile



email_pattern = (
        r"^(?!\.)"                              # Ne commence pas par un point
        r"[^\s@<>()[\]\";:,]+(?:\.[^\s@<>()[\]\";:,]+)*"  # Partie locale avec accents
        r"@"                                    # Symbole @
        r"(?:[^\W_][\w\-À-ÖØ-öø-ÿ]{0,61}[^\W_]\.)+"  # Sous-domaines autorisant accents
        r"[A-Za-zÀ-ÖØ-öø-ÿ]{2,63}$"             # TLD (entre 2 et 63 caractères, avec accents)
    )


def checkIfStringNotRequired(sentence):
    if sentence is None or str(sentence).strip() == "":
        return None
    return str(sentence).strip()


def checkIfStringRequired(key, sentence, errors):
    if sentence is None or str(sentence).strip() == "":
        errors[key] = "Ce champ est obligatoire"
        return None
    return str(sentence).strip()


def check_if_select_return_string(key, sentence, errors):
    if sentence is None or str(sentence).strip() == "":
        errors[key] = "Ce champ est obligatoire"
        return None
    sentence_str = str(sentence).strip().lower()
    if sentence_str == "0" or "choisir" in sentence_str:
        errors[key] = "Veuillez choisir une option"
        return None
    return sentence


def get_unique_oipah(key, base_query, sentence, errors, field_name="oipah"):
    if not sentence:
        errors[key] = "Ce champ est obligatoire"
    if sentence:
        filter_kwargs = {field_name: sentence}
        if base_query.filter(**filter_kwargs).exists():
            errors[key] = "Ce nom existe déjà"
    if not errors:
        return str(sentence).strip()


def checkIfEmailRequired(key, sentence, errors):
    if sentence is None or str(sentence).strip() == "":
        errors[key] = "Ce champ est obligatoire"
    sentence = str(sentence).strip()
    if re.match(email_pattern, sentence):
        return sentence
    errors[key] = "Entrez une adresse email valide"
    

def checkIfEmailRequiredForRegisterFirstTime(key, sentence, table, errors): #ceci fait une recherche sur l'ensemble des emails de la table User
    if sentence is None or str(sentence).strip() == "":
        errors[key] = "Ce champ est obligatoire"
    sentence = str(sentence).strip()
    is_valid_email = bool(re.match(email_pattern, sentence, re.UNICODE))
    email_exists = table.objects.filter(email=sentence).exists()
    if not sentence:
        errors[key] = "Ce champ est obligatoire"
    if sentence and not is_valid_email:
        errors[key] = "Entrez une adresse email valide"
    if sentence and email_exists:
        errors[key] = "Cette adresse email existe déjà"
    return sentence


def check_phone_numberRequired(key, sentence, errors):
    pattern = r'^\+\d{1,3}(?:\s?\d{1,4}){2,}$'

    if not sentence or str(sentence).strip() == "":
        errors[key] = 'Ce champ est obligatoire'
        return None

    sentence = str(sentence).strip()
    if re.match(pattern, sentence):
        return sentence
    else:
        errors[key] = "Entrez numéro valide avec indice de pays"
        return None


def check_is_only_numbers(key, param, errors):
    if not param:
        errors[key] = "Ce champ est obligatoire"
    param_str = str(param)
    is_numeric = bool(re.fullmatch(r'\d+', param_str))
    if not is_numeric:
        errors[key] = "Ce champ doit être numérique"
    if is_numeric:
        return int(param)
    

def checkIfUserAgree(key, sentence, errors):
    if not sentence:
        errors[key] = "Veuillez accepter les termes et conditions"
    return True


def passwordCheckRequired(key, passwd, lengthPassword, errors):
    SpecialSym =['$', '@', '#', '%']
    val = True
    
    if passwd == '' or passwd == None:
        errors[key] = "Ce champ est obligatoire"
    if passwd and len(passwd) < lengthPassword:
        errors[key] = f"Votre mot de passe doit contenir {lengthPassword} caractères"
        val = False
        
    if passwd and len(passwd)>= lengthPassword and not any(char.isdigit() for char in passwd):
        errors[key] = "Votre mot de passe doit contenir au moins un chiffre"
        val = False
        
    if passwd and len(passwd)>= lengthPassword and not any(char.isupper() for char in passwd):
        errors[key] = "votre mot de passe doit contenir au moins une majuscule"
        val = False
        
    if passwd and len(passwd)>= lengthPassword and not any(char.islower() for char in passwd):
        errors[key] = "votre mot de passe doit contenir au moins une minuscule"
        val = False
        
    if passwd and len(passwd)>= lengthPassword and not any(char in SpecialSym for char in passwd):
        errors[key] = "votre mot de passe doit contenir au moins un caractère ($@#)"
        val = False
    if val:
        return str(passwd)
    

ALLOWED_FORMATS = ["PNG", "JPEG", "JPG"]

def validate_base64_image(key, image_base64, errors):
    try:
        if not image_base64:
            errors[key] = "Image requise."
            return None, None

        # Supprime le préfixe éventuel
        if "," in image_base64:
            header, image_base64 = image_base64.split(",")

        # Décodage
        image_bytes = base64.b64decode(image_base64)

        # Vérification image
        image = Image.open(BytesIO(image_bytes))
        image_format = image.format.upper()

        if image_format not in ALLOWED_FORMATS:
            errors[key] = "Format d'image requis : png, jpg, jpeg."
            return None, None

        extension = "jpg" if image_format == "JPEG" else image_format.lower()

        filename = f"{uuid.uuid4()}.{extension}"

        return ContentFile(image_bytes, name=filename), extension

    except Exception:
        errors[key] = "Image invalide. Format requis : png, jpg, jpeg."
        return None, None


    