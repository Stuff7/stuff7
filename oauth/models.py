from django.db import models
from user.models import User

class OAuthUser(models.Model):
  id = models.CharField(max_length=128, primary_key=True)
  login_id = models.BigIntegerField()
  provider = models.CharField(max_length=64)
  user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=True)
  token = models.TextField()
  login = models.CharField(max_length=64)
  display_name = models.CharField(max_length=64)
  thumbnail = models.TextField()

  def save(self, *args, **kwargs):
    if not self.user:
      user = User(current_user=self.id)
      user.save()
      self.user = user

    super(OAuthUser, self).save(*args, **kwargs)

  def __str__(self):
    return (
      f"OAuth#{self.id}<"
      f"provider: {self.provider}, "
      f"login_id: {self.login_id}, "
      f"user: {self.user}, "
      f"token: {self.token}, "
      f"login: {self.login}, "
      f"display_name: {self.display_name}, "
      f"thumbnail: {self.thumbnail}>"
    )

  class Meta:
    db_table = "OAuthUser"

class OAuthCredentials(models.Model):
  id = models.CharField(max_length=64, primary_key=True)
  access_token = models.TextField()
  expires_in = models.IntegerField()
  scope = models.TextField()
  token_type = models.CharField(max_length=128)
  expires_at = models.FloatField()

  def __str__(self):
    return (
      f"OAuthCredentials#{self.id}<"
      f"access_token: {self.access_token}, "
      f"expires_in: {self.expires_in}, "
      f"scope: {self.scope}, "
      f"token_type: {self.token_type}, "
      f"expires_at: {self.expires_at}>"
    )

  class Meta:
    db_table = "OAuthCredentials"
