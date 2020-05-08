from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta as td
from calendar import isleap

from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import path, include

from babel.dates import format_datetime

from oauth.views import OAuthClient
from .textapis import TextAPI

@override_settings(ROOT_URLCONF=__name__)
class OAuthClientTestCase(TestCase):
  def setUp(self):
    self.request = Client()
    self.age = "2 years, 1 month, 16 days, 15 hours, 24 minutes, 33 seconds"
    self.date = format_datetime(test._date, format="full", locale="en")

  def test_no_follower_specified(self):
    msg = "You need to specify a follower"
    followage = self.response("followage")
    self.assertIn(msg, followage)
    followdate = self.response("followdate")
    self.assertIn(msg, followage)

  def test_followdate(self):
    response = self.response("followdate?from=someFollower")
    self.assertIn("following", response)
    self.assertIn(self.date, response)

  def test_followage(self):
    response = self.response("followage?from=someFollower")
    self.assertIn("following", response)
    self.assertIn(self.age, response)

  def test_joined(self):
    response = self.response("joined")
    self.assertIn("created", response)
    self.assertIn(self.date, response)

  def test_accountage(self):
    response = self.response("accountage")
    self.assertIn("old", response)
    self.assertIn(self.age, response)

  def test_starttime(self):
    response = self.response("starttime")
    self.assertIn("started", response)
    self.assertIn(self.date, response)

  def test_uptime(self):
    response = self.response("uptime")
    self.assertIn("live", response)
    self.assertIn(self.age, response)

  def response(self, endpoint):
    return self.request.get(f"/api/test/someChannel/{endpoint}").content.decode()

class TestOAuthClient(OAuthClient, TextAPI):
  provider = "test"

  def __init__(self):
    super().__init__()
    self.now = dt.now(tz.utc)
    self._date = self.now - td(days=self.leap(777), hours=15, minutes=24, seconds=33)
    self.channel = "TestChannel"
    self.follower = "TestFollower"

  @property
  def date(self):
    return self._date.isoformat()

  def leap(self, number):
    return number+1 if isleap(self.now.year) else number

  def account_creation(self, channel):
    """ Fetching channel creation date """
    return self.date, self.channel

  def followage(self, follower, channel):
    """ Fetching follow info """
    return self.follower, self.channel, self.date

  def uptime(self, channel):
    """ Fetching current stream info if any """
    return self.date, self.channel

test = TestOAuthClient()

urlpatterns = [
  path("api/", include(test.urlpatterns)),
]
