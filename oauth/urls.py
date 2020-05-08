from .twitch.views import twitch
from .mixer.views import mixer

urlpatterns = [
  *twitch.urlpatterns,
  *mixer.urlpatterns,
]
