from oauth.views import OAuthClient
from oauth.textapis import TextAPI

class TwitchOAuthClient(OAuthClient, TextAPI):
  """ Offers access to multiple resources from the Twitch API
  and parses them into plain text responses for bots in this
  platform to consume. """
  provider = "twitch"
  api = "https://api.twitch.tv/helix"
  oauth_url = "https://id.twitch.tv/oauth2"
  authorization_url = f"{oauth_url}/authorize"
  token_url = f"{oauth_url}/token"
  scope = ("channel:read:subscriptions",)
  
  def userinfo(self, data):
    """ Packing user info """
    return {
      "login_id":data["id"],
      "login":data["login"],
      "display_name":data["display_name"],
      "thumbnail":data["profile_image_url"],
    }

  def fetchjson(self, *args, **kwargs):
    """ Unpacking API response """
    try:
      return super().fetchjson(*args, **kwargs)["data"][0]
    except KeyError:
      raise TextAPI.InvalidLogin()

  def get_user(self, login):
    """ Fetching user id and name.

    :param str|int login: user's name or id

    :return tuple: id and username if found """
    action = { True: "id", False: "login" }
    try:
      data = self.usecreds(f"users?{action[login.isdigit()]}={login}")
      return data["id"], data["display_name"]
    except IndexError:
      raise TextAPI.UserDoesNotExist(keyword=login)

  def account_creation(self, channel):
    """ Twitch API does not give access to the account creation date """
    raise NotImplementedError

  def followage(self, follower, channel):
    """ Fetching follow info """
    follower_id, follower_name = self.get_user(follower)
    channel_id, channel_name = self.get_user(channel)

    try:
      data = self.usecreds(f"users/follows?from_id={follower_id}&to_id={channel_id}&first=1")
    except IndexError:
      raise TextAPI.NotFollowing(follower=follower_name, channel=channel_name)
    
    return data["from_name"], data["to_name"], data["followed_at"]

  def uptime(self, channel):
    """ Fetching current stream info if any """
    try:
      data = self.usecreds(f"streams?user_login={channel}")
      return data["started_at"], data["user_name"]
    except IndexError:
      channel_id, channel_name = self.get_user(channel)
      raise TextAPI.NotLive(channel=channel_name)

twitch = TwitchOAuthClient(
  include_client_id=True,
  include_client_secret=True,
  include_client_credentials=True,
)
