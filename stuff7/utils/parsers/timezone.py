from contextlib import suppress
from datetime import datetime as DT

import pytz
from babel.dates import get_timezone_location as tzlocation

from .tzdict import tzabvs

class TimezoneParser:
  """ Guessing timezone by name, abbreviations or country code. """
  _timezone = _default_timezone = "UTC"

  def __init__(self, timezone=None, default=None):
    if timezone is not None: self.timezone = timezone
    if default is not None: self._default_timezone = default

  @property
  def timezone(self):
    return self._timezone

  @timezone.setter
  def timezone(self, timezone):
    self._timezone = timezone.replace(" ", "_")

  @property
  def default_timezone(self):
    return self._default_timezone

  def parsetz(self, *args, **kwargs):
    return pytz.timezone(self.parse(*args, **kwargs))

  def parse(self, timezone, country_code=""):
    """ Parsing timezone from arbitrary input string.

    :param str timezone: String to parse into an actual timezone
    :param str country_code: Filter timezones by this country code """
    self.timezone = timezone
    
    # The input is an actual timezone!
    if self.timezone.title() in pytz.all_timezones:
      return self.timezone

    # Try to guess the timezone as an offset
    with suppress(ValueError):
      return self.find_by_offset()

    # Try looking by abbreviation using the country
    # to narrow down the search if any
    with suppress(ValueError):
      country_tzones = pytz.country_timezones.get(country_code)
      set_zones = self.find_by_abv(country_tzones)
      return max(set_zones, key=len)

    # Try looking through the most common abbreviations
    # not included in pytz
    with suppress(KeyError):
      return tzabvs[self.timezone.upper()]

    # Try to find timezones with similar names
    with suppress(ValueError):
      return self.find_by_similar_name()

    # Could not find timezone
    return self.default_timezone

  def find_by_offset(self):
    """ Try to find a timezone by offset. """
    offset = int(self.timezone)*-1
    if offset < -14 or offset > 12:
      raise ValueError(f"{offset} is not a valid offset")
    if offset > 0:
      offset = "+" + str(offset)
    else:
      offset = str(offset)
    return "Etc/GMT" + offset

  def find_by_abv(self, timezones=None):
    """ Try to find a timezone using common timezone abbreviations. """
    if timezones is None: timezones = pytz.all_timezones
    abbrev = self.timezone.upper()
    countries = set()
    for name in timezones:
      tzone = pytz.timezone(name)
      for utcoffset, dstoffset, tzabbrev in getattr(
        tzone, "_transition_info", [[None, None, DT.now(tzone).tzname()]]):
        if tzabbrev.upper() == abbrev:
          countries.add(name)
    return countries

  def find_by_similar_name(self):
    """ Try to find a timezone by similar names. """
    tz = self.timezone.lower()
    for tzname in pytz.all_timezones:
      if tz in tzname.lower():
        return tzname
    raise ValueError("Timezone not found")
