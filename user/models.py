from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from stuff7.settings import LANGUAGES

class User(AbstractBaseUser, PermissionsMixin):
  USERNAME_FIELD = "id"

  current_user = models.CharField(max_length=128)
  language = models.CharField(max_length=8, choices=LANGUAGES, default="en-US")
  palette = models.CharField(default="dark:#3f51b5:#f50057",max_length=32)

  """ This will store the list of series the user has saved
  in a JSON string.
  There's no need to add columns to the database since it's
  only gonna be read/written and never queried.
  Validation of this data will be done in the view using DRF. """
  series_list = models.TextField(default="[]")

  password = None

  def __str__(self):
    return (
      f"User#{self.id}<"
      f"current_user: {self.current_user}, "
      f"language: {self.language}, "
      f"palette: {self.palette}>"
    )

  class Meta:
    db_table = "User"
