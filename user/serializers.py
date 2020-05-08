from rest_framework import serializers
from oauth.serializers import OAuthUserSerializer
from collections import OrderedDict
from .models import User

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
  profiles = OAuthUserSerializer(source="oauthuser_set", many=True, required=False, read_only=True)
  current_user = serializers.CharField(max_length=128, required=False)

  class Meta:
    model = User
    fields = ("id", "current_user", "is_authenticated", "language", "palette", "profiles")
    read_only_fields = ("id", "is_authenticated", "profiles")
