from functools import wraps
from datetime import datetime
from contextlib import suppress

from django.http import HttpResponse
from requests.exceptions import ReadTimeout
from dateutil.parser import parse

from babel.core import UnknownLocaleError
from babel.dates import format_datetime
from pytz.exceptions import UnknownTimeZoneError

from stuff7.utils.parsers import TimeDeltaParser, TimezoneParser
from stuff7.utils.collections import safeformat

class TextAPI:
  """ Provides generic Text APIs to use with chatbots in live streaming platforms.
  This only provides generic functions to handle all the custom API features
  that this project provides. It's necessary to subclass TextAPI and define
  the functions to get the info from the chosen API and return it so the
  generic functions defined in here can use it. """
  provider = None
  # Parses time difference strings
  delta = TimeDeltaParser()
  # Parses timezones
  tz = TimezoneParser()

  # Default API responses used when no query params are found
  user_not_found_msg = "No users found with the name or id \"{keyword}\""
  invalid_login_msg = "Invalid username."
  followage_msg = (
    "{follower} has been following {channel} for "
    "<{years} year{years(s)}>, <{months} month{months(s)}>, "
    "<{days} day{days(s)}>, <{hours} hour{hours(s)}>, "
    "<{minutes} minute{minutes(s)}>, <{seconds} second{seconds(s)}> "
    "and <{microseconds}μs>."
  )
  followdate_msg = "{follower} started following {channel} on {date}"
  followage_error = "{follower} is not following {channel}"
  uptime_msg = (
    "{channel} has been live for <{years} year{years(s)}>, "
    "<{months} month{months(s)}>, <{days} day{days(s)}>, "
    "<{hours} hour{hours(s)}>, <{minutes} minute{minutes(s)}>, "
    "<{seconds} second{seconds(s)}> and <{microseconds}μs>."
  )
  starttime_msg = "{channel} started their current stream on {date}"
  uptime_error = "{channel} is not live"
  accountage_msg = (
    "{channel}'s account is <{years} year{years(s)}>, "
    "<{months} month{months(s)}>, <{days} day{days(s)}>, "
    "<{hours} hour{hours(s)}>, <{minutes} minute{minutes(s)}>, "
    "<{seconds} second{seconds(s)}> and <{microseconds}μs> old."
  )
  joined_msg = "{channel}'s account was created on {date}"

  def _textapi(fn):
    """ Handles common API request exceptions

    :param Callable[[self, params, **kwargs], str] fn: Handler for the request.
    :return Callable[[self, request, **wargs], HttpResponse]: A decorator to
    handle the request and the most common exceptions. """
    @wraps(fn)
    def decorator(self, request, **kwargs):
      """ Handles common exceptions with Http requests

      :request: Current http request
      
      :return: Http text/plain response using the string returned from fn
               as content or an error message if there was an exception. """
      response = HttpResponse(content_type="text/plain; charset=UTF-8")
      write = response.write
      params = request.GET
      try:
        write(fn(self, params, **kwargs))
      except NotImplementedError:
        write(f"The {self.provider.capitalize()} API does not give access to this information.")
      except ReadTimeout:
        write(f"External request to {self.provider.capitalize()} servers timed out. Try again.")
      except TextAPI.UserDoesNotExist as e:
        write(safeformat(params.get("not_found", self.user_not_found_msg),
          keyword=e.keyword))
      except TextAPI.NotFollowing as e:
        write(safeformat(params.get("error_msg", self.followage_error),
          channel=e.channel, follower=e.follower))
      except TextAPI.NotLive as e:
        write(safeformat(params.get("error_msg", self.uptime_error),
          channel=e.channel))
      except TextAPI.InvalidLogin as e:
        write(params.get("error_msg", self.invalid_login_msg))
      return response
    return decorator

  def _follow_date(fn):
    @wraps(fn)
    def follow_decorator(self, params, channel):
      """ Handles actions related to follow dates.
      This is a generic function, you need to define the function
      "followage" which takes 2 parameters (follower, channel) both are
      arbitrary strings provided by the user which have to be used
      to get the the follower, channel and date of follow from the API

      :param QueryString params: Optional query params
        :queryparam str from: The follower's name (required)

      :param channel: Channel's name """
      follower = params.get("from")
      if follower is None:
        return "You need to specify a follower."

      follower_name, channel_name, date = self.followage(follower, channel)
      action, default_msg = fn(self, params, channel)

      return action(default_msg, params, date,
        follower=follower_name, channel=channel_name)
    return follow_decorator

  def _channel_date(fn):
    @wraps(fn)
    def channel_date_decorator(self, params, channel):
      """ Formatting a date belonging to a channel.
      Must define both account_creation and uptime functions. They take 1
      parameter which is the channel name to search. And must also
      return a tuple consisting of a date and the channel name

      :param channel: Channel's name """
      action, default_msg, channel_date = fn(self, params, channel)
      date, channel_name = channel_date(channel)
      return action(default_msg, params, date, channel=channel_name)
    return channel_date_decorator

  @_textapi
  @_follow_date
  def _followdate(self, params, channel):
    """ Formatting the date a user started following. """
    return self._formatdate, self.followdate_msg

  @_textapi
  @_follow_date
  def _followage(self, params, channel):
    """ Calculating the time a user has followed a channel. """
    return self._timespan, self.followage_msg

  @_textapi
  @_channel_date
  def _joined(self, params, channel):
    """ Formatting account creation date. """
    return self._formatdate, self.joined_msg, self.account_creation

  @_textapi
  @_channel_date
  def _accountage(self, params, channel):
    """ Calculating the time since a user created their account. """
    return self._timespan, self.accountage_msg, self.account_creation

  @_textapi
  @_channel_date
  def _starttime(self, params, channel):
    """ Formatting the date at which the current live stream started. """
    return self._formatdate, self.starttime_msg, self.uptime

  @_textapi
  @_channel_date
  def _uptime(self, params, channel):
    """ Calculating the time a user has been live streaming. """
    return self._timespan, self.uptime_msg, self.uptime

  def _timespan(self, default_msg, params, date, **options):
    """ Calculating the timespan between a date and now.

    :param str default_msg: Message to be used and formatted if there's no msg in the query string
    :param QueryString params: Query parameters from the request
      :queryparam str msg: User provided message to be formatted
    :param str date: Date from which the timespan will be calculated
    :param dict options: Keywords to replace in the string

    :return str: Formatted timespan """
    date = parse(date)
    msg = params.get("msg", default_msg)
    parsed = self.delta.parse(msg, datetime.now(tz=date.tzinfo), date)

    return safeformat(parsed, **options)

  def _formatdate(self, default_msg, params, date, **options):
    """ Formatting a date.
    Supports most locales/timezones/formats.

    :param QueryString params: Optional query params
      :queryparam str tz: Date will be displayed in this timezone (Default: UTC)
      :queryparam str format: Date format, can be short, medium, long or full (Default: full)
      :queryparam str locale: Date will be displayed using this language (Default: en)
    :param str channel: Channel's name """
    date = parse(date)

    with suppress(UnknownTimeZoneError, KeyError):
      date = date.astimezone(self.tz.parsetz(*params["tz"].split("_")[:2]))

    msg = params.get("msg", default_msg)
    date_format = params.get("format", "full")
    date_locale = params.get("locale", "en")

    try:
      date = format_datetime(date, format=date_format, locale=date_locale)
    except (UnknownLocaleError, ValueError):
      date = format_datetime(date, format=date_format, locale="en")
    except KeyError as e:
      return (
        f"There was an error parsing the date: {e}. "
        "Try one of the following format options: "
        "short, medium, long, full."
      )

    return safeformat(msg, date=date, **options)

  class APIError(Exception):
    def __init__(self, **kwargs):
      for k, v in kwargs.items():
        setattr(self, k, v)

  class NotFollowing(APIError):
    pass

  class NotLive(APIError):
    pass

  class UserDoesNotExist(APIError):
    pass

  class InvalidLogin(APIError):
    pass
