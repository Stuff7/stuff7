from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta as td
from calendar import isleap

from unittest import TestCase

from pytz import timezone

from . import TimeDeltaParser, TimezoneParser

class TimeDeltaParserTestCase(TestCase):
  def setUp(self):
    self.delta = TimeDeltaParser()
    self.timeunits = ("years", "months", "days", "hours", "minutes", "seconds", "microseconds")
    self.now = dt.now(tz.utc)
    self.msg = (
      "{channel} <{years} year{years(s)}>, "
      "<{months} month{months(s)}>, <{days} day{days(s)}>, "
      "<{hours} hour{hours(s)}>, <{minutes} minute{minutes(s)}> "
      "and <{seconds} second{seconds(s)}>"
    )
    self.date = self.now - td(days=self.leap(777), hours=15, minutes=24, seconds=33)
    self.strid = "someID"

  def test_parse_ok(self):
    parsedresult = self.delta.parse(self.msg, self.now, self.date)
    self.assertEqual(parsedresult, "{channel} 2 years, 1 month, 16 days, 15 hours, 24 minutes and 33 seconds")
    parsedresult = self.delta.parse(self.msg, self.now, self.now-td(days=self.leap(365), seconds=33))
    self.assertEqual(parsedresult, "{channel} 1 year and 33 seconds")
    parsedresult = self.delta.parse((
      "{channel} <{years} year{years(s)}>, "
      "<{months} month{months(s)}>, "
      "<{days} day{days(s)}> and "
      "[{hours:02d}:{minutes:02d}:{seconds:02d} hours]"),
      self.now, self.now-td(days=self.leap(365), seconds=33)
    )
    self.assertEqual(parsedresult, "{channel} 1 year and 00:00:33 hours")
    parsedresult = self.delta.parse(f"Escape \<block\> identifiers like \[this\].", self.now, self.date)
    self.assertEqual(parsedresult, "Escape <block> identifiers like [this].")

  def test_parse_invalid_format(self):
    parsedresult = self.delta.parse("Can't use single {", self.now, self.date)
    self.assertIn("Invalid string", parsedresult)
    parsedresult = self.delta.parse("Can't use single } either", self.now, self.date)
    self.assertIn("Invalid string", parsedresult)

  def test_parse_parser_error(self):
    parsedresult = self.delta.parse("[You should close your blocks..", self.now, self.date)
    self.assertIn("Expecting ].", parsedresult)
    parsedresult = self.delta.parse("Closing inexistent blocks isn't allowed..>", self.now, self.date)
    self.assertIn("Single > is not allowed.", parsedresult)

  def test_timediff(self):
    parsedobj = self.delta.timediff(self.now, self.date)
    self.assertEqual(tuple(parsedobj), self.timeunits)
    self.assertEqual(tuple(parsedobj.values()), (2, 1, 16, 15, 24, 33, 0))

  def test_loop(self):
    self.assertEqual(len(tuple(x for x in self.delta.loop("Some string without any blocks."))), 2,
      msg="Beginning and end of string are always shown after parsed is done.")
    parsed = tuple(x for x in self.delta.loop(self.msg))
    self.assertTrue(all(type(obj) is self.delta.Block for obj in parsed[1:-1]),
      msg="Anything in between the parsed result is a block.")

  def test_split_ok(self):
    parts = self.delta.split("<Some block [inner [blocks]] and an \[escaped block> and <\<another> [block\>]")
    self.assertEqual(len(parts), 7,
      msg="Returns 3 blocks with connectors 3*2=6. And a string. So 3*2+1=7 total parts.")
    self.assertEqual(parts[1], "<Some block [inner [blocks]] and an [escaped block>")
    self.assertEqual(parts[3], "<<another>")
    self.assertEqual(parts[5], "[block>]")

  def test_split_error(self):
    with self.assertRaises(ValueError) as e:
      self.delta.split("<Some invalid block>>")
    self.assertEqual("Single > is not allowed.", str(e.exception))
    with self.assertRaises(ValueError) as e:
      self.delta.split("[Some invalid block")
    self.assertEqual("Expecting ].", str(e.exception))

  def leap(self, number):
    return number+1 if isleap(self.now.year) else number

class TimezoneParserTestCase(TestCase):
  def setUp(self):
    self.tz = TimezoneParser()
    self.utc = dt.now(tz.utc)
    self.common_tzones = {
      "gmt": self.tzone("iceland"),
      "aoe": self.tzone("Etc/GMT+12"),
      "pst_us": self.tzone("America/Los_Angeles"),
      "pdt_us": self.tzone("America/Los_Angeles"),
      "cst": self.tzone("America/Chicago"),
      "cdt": self.tzone("America/Chicago"),
      "ast": self.tzone("America/Halifax"),
      "adt": self.tzone("America/Halifax"),
      "est": self.tzone("America/New_York"),
      "edt": self.tzone("America/New_York"),
      "mst": self.tzone("America/Edmonton"),
      "mdt": self.tzone("America/Edmonton"),
      "akst": self.tzone("America/Anchorage"),
      "akdt": self.tzone("America/Anchorage"),
      "aest": self.tzone("Australia/Sydney"),
      "acst": self.tzone("Australia/Adelaide"),
      "acdt": self.tzone("Australia/Adelaide"),
      "awst": self.tzone("Australia/Perth"),
      "bst": self.tzone("Europe/London"),
      "ist": self.tzone("Europe/Dublin"),
      "wet": self.tzone("Europe/Lisbon"),
      "west": self.tzone("Europe/Lisbon"),
      "cet": self.tzone("Europe/Brussels"),
      "cest": self.tzone("Europe/Brussels"),
      "eet": self.tzone("Europe/Bucharest"),
      "eest": self.tzone("Europe/Bucharest"),
    }
    self.tzoffsets = {
      **{ str(offset*-1): self.tzone(f"Etc/GMT{offset}") for offset in range(-14, 0) },
      **{ str(offset*-1): self.tzone(f"Etc/GMT+{offset}") for offset in range(0, 12+1) },
    }

  def test_parse_common_timezones(self):
    for abbv, date in self.common_tzones.items():
      guess_tzone = self.tz.parsetz(*abbv.split("_")[:2])
      guess_date = self.utc.astimezone(guess_tzone)
      self.assertEqual(guess_date, date,
        msg="Parses common timezone correctly.")

  def test_find_by_offset(self):
    for offset, date in self.tzoffsets.items():
      self.tz.timezone = offset
      guess_date = self.tzone(self.tz.find_by_offset())
      self.assertEqual(guess_date, date,
        msg="Parses all timezone offsets.")

  def tzone(self, tz):
    return self.utc.astimezone(timezone(tz))
