import json
from collections import namedtuple
from contextlib import suppress

from django.db import OperationalError
from django.db.utils import ProgrammingError
from django.shortcuts import redirect
from django.contrib.auth import login
from django.forms.models import model_to_dict
from django.urls import path

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from stuff7.settings import host, env
from oauth.models import OAuthCredentials
from oauth.models import OAuthUser

class OAuthClient:
  """ Base class for all OAuth 2 clients """
  # Subclass and set these attributes as well as the userinfo method
  provider = None
  api = None
  authorization_url = None
  token_url = None
  refresh_url = None
  scope = None
  endpoints = {}

  def __init__(self, include_client_id=None, include_client_secret=None, include_client_credentials=None):
    """ Constructs a new OAuth 2 Client """
    PROVIDER = self.provider.upper()
    self.client_id = env(f"{PROVIDER}_CLIENT_ID")
    self.client_secret = env(f"{PROVIDER}_CLIENT_SECRET")
    self.redirect_uri = f"{host}/api/oauth/{self.provider}/check/"
    self.state = f"{self.provider}_oauth_state"
    
    if self.refresh_url is None: self.refresh_url = self.token_url

    self.options = {
      "include_client_id": include_client_id,
      "client_secret": include_client_secret and self.client_secret,
      "scope": self.scope,
    }
    
    # Can throw exception on first migration. Nothing to worry about.
    with suppress(OperationalError, ProgrammingError):
      if include_client_credentials:
        self.get_credentials()

  def authorize(self, request):
    """ Redirect user to provider for authorization """
    client = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=self.redirect_uri)
    authorization, request.session[self.state] = client.authorization_url(self.authorization_url)
    return redirect(authorization)

  def check(self, request):
    """ Retrieve an access token.

    The user has been redirected back from the provider to the registered
    callback URL /api/oauth/{provider}/check/. We'll use the code included
    in the redirect URL to obtain an access token.
    """
    client = OAuth2Session(self.client_id, state=request.session[self.state], redirect_uri=self.redirect_uri)
    url = request.build_absolute_uri()
    token = client.fetch_token(self.token_url, **self.options, authorization_response=url)
    info = self.userinfo(self.fetchjson("users", token))
    defaults = { "provider":self.provider, "token":json.dumps(token), **info }

    return self.update(request, defaults)

  def update(self, request, defaults):
    """ Updating OAuthUser
    
    Updates oauth user info in database and links it
    to the current user if possible
    """
    oauthid = f'{self.provider}:{defaults["login_id"]}'
    user = request.user
    # When user is authenticated and the oauth user
    # is new, try to link it to current user
    if user.is_authenticated:
      # Not using update_or_create because that would also
      # change the owner of the account
      oauth, created = OAuthUser.objects.get_or_create(
        id=oauthid, defaults={**defaults, "user": user},
      )
      # If it already exists update user info
      if not created:
        for k,v in defaults.items():
          setattr(oauth, k, v)
        oauth.save()
        # Redirect with an error if someone else owns the account
        if not user.oauthuser_set.filter(id=oauthid).exists():
          return redirect("/?error=already_linked")
      # Everything is fine, switch the current user to the linked account
      user.current_user = oauthid
      user.save()
    
    # If not authenticated just login the user,
    # creating a new user if needed
    else:
      oauth, created = OAuthUser.objects.update_or_create(
        id=oauthid, defaults=defaults,
      )
      oauth.user.current_user = oauthid
      oauth.user.save()
      login(request, oauth.user)

    return redirect("/")

  def endpoint(self, name):
    """ Getting API endpoint.

    :param str name: Endpoint name or raw endpoint

    :return str: Full API endpoint """
    return f"{self.api}/{self.endpoints.get(name, name)}"

  def pubfetch(self, resource):
    """ Fetching public API resource.

    :param str resource: Resource name or raw endpoint

    :return dict: JSON response for the API resource if any """
    return OAuth2Session(self.client_id).get(self.endpoint(resource)).json()

  def fetchjson(self, resource, token, token_updater=None):
    """ Fetching protected API resource.

    :param str resource: Resource name or raw endpoint
    :param dict token: Token object for authentication
    :param Callable[[token], None] token_updater: What to do
    if the token gets updated

    :return OAuth2Session: """
    return OAuth2Session(
      self.client_id,
      token=token,
      token_updater=token_updater or self.token_updater,
    ).get(self.endpoint(resource), headers={"Client-ID": self.client_id}).json()

  def token_updater(self, token):
    pass

  def credentials_updater(self, token):
    """ Updating client credentials token.

    :param dict token: Updated token """
    OAuthCredentials.objects.get(pk=self.provider).update(**self.stringify(token))
    self.credentials = token

  def usecreds(self, resource):
    """ Fetching protected API resource using client credentials.

    :param str resource: Resource name or raw endpoint

    :return dict: JSON response for the API resource if any """
    return self.fetchjson(resource, self.credentials, self.credentials_updater)

  def get_credentials(self):
    """ Getting/Creating client credentials in database. """
    try:
      credentials = OAuthCredentials.objects.get(pk=self.provider)
      self.credentials = model_to_dict(credentials, fields=(
        "access_token", "expires_in", "scope", "token_type", "expires_at"
      ))
    except OAuthCredentials.DoesNotExist:
      client = OAuth2Session(self.client_id, client=BackendApplicationClient(self.client_id), scope=self.scope)
      self.credentials = client.fetch_token(self.token_url, **self.options)
      fields = { "id": self.provider, **self.stringify(self.credentials) }
      credentials = OAuthCredentials(**fields)
      credentials.save()

  def urls(self, url, name, resources, prefix=""):
    """ Creating local endpoints for current provider.

    :param str url: Endpoint format
    :param str name: Endpoint name
    :param tuple|dict resources: Resources to be created for this endpoint
    :param str prefix: Prefix to be used in case function view is named
    differently from resource

    :return list: List of paths """
    if type(resources) == tuple:
      resource_generator = ((resource, resource) for resource in resources)
    elif type(resources) == dict:
      resource_generator = ((resource, func) for resource, func in resources.items())
    else: return

    return [
      path(
        url.format(provider=self.provider, resource=resource), getattr(self, f"{prefix}{resource}"),
        name=f"{self.provider}-{name}".format(provider=self.provider, resource=resource),
      ) for resource, func in resource_generator if hasattr(self, func)
    ]

  @property
  def urlpatterns(self):
    """ Creating urlpatterns for current OAuth 2 client. """
    oauth = ("authorize", "check")
    api = {
      "joined": "account_creation",
      "accountage": "account_creation",
      "followage": "followage",
      "followdate": "followage",
      "uptime": "uptime",
      "starttime": "uptime",
    }

    return [
      *self.urls(url="oauth/{provider}/{resource}/", name="oauth-{resource}", resources=oauth),
      *self.urls(url="{provider}/<channel>/{resource}", name="{resource}", resources=api, prefix="_"),
    ]

  def stringify(self, token):
    """ Stringifying scope from token object.

    :param dict token: Token object to have scope stringified """
    return { **token, "scope": json.dumps(token["scope"]) }

  def userinfo(self, data):
    """Parse data from API response. (Must implement in subclass)

    :param data: Raw JSON response from API.
    :return dict: User info containing the following keys {
      "login_id": int,
      "login": string,
      "display_name": string,
      "thumbnail": string,
    } """
    raise NotImplementedError()
