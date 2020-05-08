import json

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import logout

from .twitch.views import twitch
from .mixer.views import mixer
from .models import OAuthUser

class OAuthUserTestCase(TestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.oauth = OAuthUser(id=id1, **defaults1)
    self.oauth.save()
    self.user = self.oauth.user

  def test_link_new_user(self):
    request = self.factory.get("/")
    request.user = self.user

    response = mixer.update(request, defaults2)

    self.assertEqual(self.user.oauthuser_set.all().count(), 2,
      msg="current user now has 2 linked oauth users")
    self.assertEqual(self.user.current_user, id2,
      msg="current selected user is now id2")
    self.assertEqual(response.url, "/",
      msg="redirects on success")

  def test_switch_user(self):
    request = self.factory.get("/")
    request.user = self.user

    OAuthUser(id=id2, user=self.user, **defaults2).save()
    response = mixer.update(request, {**defaults2, "thumbnail":"new_thumbnail"})

    self.assertEqual(self.user.oauthuser_set.all().count(), 2,
      msg="same users since is just an update")
    self.assertEqual(self.user.current_user, "mixer:2",
      msg="switch user")
    self.assertEqual(self.user.oauthuser_set.get(id=self.user.current_user).thumbnail, "new_thumbnail",
      msg="updates thumbnail")

  def test_link_existing_user(self):
    request = self.factory.get("/")
    oauth = OAuthUser(id=id2, **defaults2)
    oauth.save()
    request.user = self.user

    response = mixer.update(request, {**defaults2, "display_name":"UpdatedName"})
    
    oauth.refresh_from_db()
    self.assertEqual(request.user.oauthuser_set.all().count(), 1,
      msg="logged in user still only has 1 linked user")
    self.assertEqual(oauth.user.oauthuser_set.all().count(), 1,
      msg="the other user still only has 1 linked user")
    self.assertEqual(oauth.display_name, "UpdatedName",
      msg="database is updated even when the user wasn't linked")
    self.assertEqual(response.url, "/?error=already_linked",
      msg="redirects with already_linked error")

  def test_register(self):
    request = self.factory.get("/")
    SessionMiddleware().process_request(request)
    request.user = AnonymousUser()

    response = mixer.update(request, defaults2)
    self.assertTrue(request.user.is_authenticated,
      msg="login successful")
    self.assertEqual(OAuthUser.objects.all().count(), 2,
      msg="new user added to database")
    self.assertEqual(response.url, "/",
      msg="redirect on success")

  def test_login(self):
    request = self.factory.get("/")
    SessionMiddleware().process_request(request)
    request.user = AnonymousUser()

    response = twitch.update(request, defaults1)
    self.assertTrue(request.user.is_authenticated,
      msg="login successful")
    self.assertEqual(OAuthUser.objects.all().count(), 1,
      msg="same users in database since it was an existing user login")
    self.assertEqual(response.url, "/",
      msg="redirect on success")

  def test_logout(self):
    request = self.factory.get("/")
    SessionMiddleware().process_request(request)
    request.user = self.user

    logout(request)
    self.assertTrue(request.user.is_anonymous,
      msg="logout successful")

token1 = {
  "access_token": "access1",
  "expires_in": 123,
  "refresh_token": "refresh1",
  "scope": ["scope:1"],
  "token_type": "bearer",
  "expires_at": 12.34,
}

token2 = {
  "access_token": "access2",
  "expires_in": 456,
  "refresh_token": "refresh2",
  "scope": ["scope:2"],
  "token_type": "bearer",
  "expires_at": 56.78,
}

defaults1 = {
  "login_id":1,
  "provider":"twitch",
  "token":json.dumps(token1),
  "login":"numberone",
  "display_name":"NumberOne",
  "thumbnail":"https://example.com/thumbnail1",
}
id1 = f"{twitch.provider}:{defaults1['login_id']}"

defaults2 = {
  "login_id":2,
  "provider":"mixer",
  "token":json.dumps(token2),
  "login":"numbertwo",
  "display_name":"NumberTwo",
  "thumbnail":"https://example.com/thumbnail2",
}
id2 = f"{mixer.provider}:{defaults2['login_id']}"
