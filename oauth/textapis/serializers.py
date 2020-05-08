from rest_framework import serializers

# Serializers define the API representation.
class CustomAPIsSerializer(serializers.Serializer):
  providers = serializers.SerializerMethodField()
  apis = serializers.SerializerMethodField()

  class Meta:
    read_only_fields = fields = ("providers", "apis")

  def __init__(self):
    """ Initialize with empty object to
    get default values all the time """
    super().__init__({})

  def get_providers(self, obj):
    return providers

  def get_apis(self, obj):
    return apis

PROVIDERS = (
  "twitch",
  "mixer",
)

TEXT_APIS = (
  ("followage", "Follow Age", ("follow", "general")),
  ("followdate", "Follow Date", ("follow", "general", "format")),
  ("accountage", "Account Age", ("general",)),
  ("joined", "Join Date", ("general", "format")),
  ("uptime", "Uptime", ("general",)),
  ("starttime", "Stream Start", ("general", "format")),
)

def named_resource(name, display_name):
  """ Packaging a named resource

  :param str name: Resource name identifier
  :param str display_name: Human-readable resource name

  :return dict: A named resource """
  return {
    "name": name,
    "display_name": display_name,
  }

def param(name, display_name, required=False):
  """ Packaging query param details

  :param str name: Raw param name
  :param str display_name: Human-readable param name
  :param bool required: Whether this param needs to
  be present in the request or not

  :return dict: Param details """
  return {
    **named_resource(name, display_name),
    "required": required,
  }

PARAM = {
  "general": [
    param("msg", "Message"),
    param("not_found", "Not Found Message"),
    param("error_msg", "Error Message"),
  ],
  "follow": [
    param("from", "From", True),
  ],
  "format": [
    param("tz", "Time Zone"),
    param("format", "Date Format"),
    param("locale", "Date Language"),
  ],
}

def provider(name):
  """ Packaging provider details

  :param str name: Provider's name

  :return dict: Provider details """
  return named_resource(name, name.capitalize())

def api(name, display_name, params):
  """ Packaging API details

  :param str name: API name identifier
  :param str display_name: Human-readable API name
  :param tuple params: List of params supported by this API

  :return dict: API details """
  return {
    **named_resource(name, display_name),
    "params": [x for p in params for x in PARAM[p]],
  }

providers = [provider(p) for p in PROVIDERS]

apis = [api(*api_details) for api_details in TEXT_APIS]
