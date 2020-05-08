from rest_framework import serializers

from .models import OAuthUser

# Serializers define the API representation.
class OAuthUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = OAuthUser
    fields = ["id", "login_id", "provider", "login", "display_name", "thumbnail"]
