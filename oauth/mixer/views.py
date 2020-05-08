from oauth.views import OAuthClient
from oauth.textapis import TextAPI

class MixerOAuthClient(OAuthClient, TextAPI):
  """ Offers access to multiple resources from the Mixer API
  and parses them into plain text responses for bots in this
  platform to consume. """
  provider = "mixer"
  mixer = "https://mixer.com" 
  api = f"{mixer}/api/v1"
  authorization_url = f"{mixer}/oauth/authorize"
  token_url = f"{api}/oauth/token"
  scope = ("subscription:view:self",)
  endpoints = { "users": "users/current" }
  
  def userinfo(self, data):
    """ Packing user info """
    return {
      "login_id":data["id"],
      "login":data["username"],
      "display_name":data["username"],
      "thumbnail":data["avatarUrl"],
    }

  def get_channel(self, channel):
    """ Fetching channel info.

    :param str|int channel: Channel's name or id

    :return dict: Channel info if found """
    channel_info = self.pubfetch(f"channels/{channel}")
    if "error" in channel_info:
      raise TextAPI.UserDoesNotExist(keyword=channel)
    return channel_info

  def account_creation(self, channel):
    """ Fetching channel creation date """
    channel_info = self.get_channel(channel)
    return channel_info["createdAt"], channel_info["token"]

  def followage(self, follower, channel):
    """ Fetching follow info """
    channel_info = self.get_channel(channel)
    try:
      data = self.pubfetch(f"channels/{channel_info['id']}/follow?where=username:eq:{follower}")[0]
    except IndexError:
      follower_info = self.get_channel(follower)
      raise TextAPI.NotFollowing(channel=channel_info["token"], follower=follower_info["token"])

    return data["username"], channel_info["token"], data["followed"]["createdAt"]

  def uptime(self, channel):
    """ Fetching current stream info if any """
    channel_info = self.get_channel(channel)
    try:
      data = self.pubfetch(f"channels/{channel_info['id']}/broadcast")
      return data["startedAt"], channel_info["token"]
    except KeyError:
      raise TextAPI.NotLive(channel=channel_info["token"])

mixer = MixerOAuthClient(
  include_client_id=True,
  include_client_secret=True,
)
