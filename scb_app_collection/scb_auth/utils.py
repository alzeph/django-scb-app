from rest_framework.test import APIClient
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

import random
from pathlib import Path
import mimetypes
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from django.contrib.auth.models import User


def login_user_in_test(user: User) -> APIClient:
    """
    Crée un objet APIClient connecté avec un utilisateur donné.

    Le cookie HttpOnly est créé comme le ferait le backend, avec les
    clés 'access' et les valeurs 'httponly', 'secure' et 'samesite'.

    :param user: L'utilisateur à connecter
    :type user: User
    :return: Un objet APIClient connecté avec l'utilisateur
    :rtype: APIClient
    """
    client = APIClient()
    token = RefreshToken.for_user(user)
    
    access = str(token.access_token)
    refresh = str(token)
    
    # Crée le cookie HttpOnly comme le ferait le backend si le httpOnly est activer dans les params
    client.cookies["access"] = str(access)
    client.cookies["access"]["httponly"] = True
    client.cookies["access"]["secure"] = True  
    client.cookies["access"]["samesite"] = "None"
    
    client.cookies["refresh"] = refresh
    # client.cookies["refresh"]["httponly"] = True
    # client.cookies["refresh"]["secure"] = True  
    # client.cookies["refresh"]["samesite"] = "None"
    

    return client
