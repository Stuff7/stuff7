import re
from collections import namedtuple

from dateutil.relativedelta import relativedelta

from stuff7.utils.collections import PluralDict

class TimeDeltaParser:
  """ Parses strings containing time units representing
  the time difference between 2 dates. """

  """ A Block specifies how to display a time unit
  and the text surrounding it.

  :param str connector: The text surrounding the time unit
  :param str var: The text containing the time unit
  :param bool show: Whether to show this block or not """
  Block = namedtuple("Block", "connector var show")
  # These characters define when a block starts
  opening = tuple("<[")
  # These characters define when a block ends
  closing = tuple(">]")
  mapping = dict(zip(opening, closing))
  units = ("years", "months", "days", "hours", "minutes", "seconds", "microseconds")
  # Pattern to search for any time unit
  any_unit = fr"(?<={{)({'|'.join(units)})(?=}}|:)"

  def parse(self, msg, date1, date2, **kwargs):
    """ Parsing time units in string.

    :param str msg: Text to parse
    :param datetime date1: lhs date
    :param datetime date2: rhs date

    :return str: Parsed text """
    diff = self.timediff(date1, date2)
    """ All the time units supporting custom parsing to handle 
    plural words in any language. """
    data = PluralDict(diff)
    parsed = ""
    # Whether there's a block already present in the text
    block_in = False
    try:
      for block in self.loop(msg):
        if type(block) is str:
          parsed+=block
          continue
        try: show = block.show or diff.get(re.search(self.any_unit, block.var).group())
        except AttributeError: show = False
        if show:
          if block_in: parsed+=block.connector
          else: block_in = True
          parsed+=block.var
      return parsed.format_map(data)
    except (ValueError) as e:
      return f"Invalid string: {e}"

  def timediff(self, a, b):
    """ Stripping unnecessary attributes from relative delta.

    :param datetime a: lhs date
    :param datetime b: rhs date

    :return dict: Dictionary containing all time units """
    difference = relativedelta(a, b)
    return { attr: getattr(difference, attr) for attr in self.units }

  def loop(self, msg):
    """ Parsing tokens into blocks.

    :param str msg: Text to parse into tokens

    :yield Block: A block holding the time unit value and
    specifying whether to show the time unit along with
    their connectors or not """
    arr = self.split(msg)
    length = len(arr)
    yield arr[0]
    arr[0] = ""
    for x in range(0, length, 2):
      yield self.Block(arr[x], arr[x+1][1:-1], arr[x+1][0]=="[") if x+1 < length else arr[x]

  def split(self, dateformat):
    """ Splitting a string into tokens.
    
    :param str dateformat: Text to be splitted

    :return list: Splitted string and tokens """
    blocks = []
    output = ""
    queue = []
    ignore = False
    for i, c in enumerate(dateformat):
      if c == "\\":
        ignore = True
        continue
      output+=c
      if ignore: ignore = False
      elif c in self.opening:
        if not queue:
          blocks.append(output[:-1])
          output = c
        queue.append(self.mapping[c])
      elif c in self.closing:
        try:
          if queue[-1] == c: del queue[-1]
        except IndexError as e:
          raise ValueError(f"Single {c} is not allowed.") from e
        if not queue:
          blocks.append(output)
          output = ""
    blocks.append(output)
    if queue:
      raise ValueError(f"Expecting {queue[0]}.")
    return blocks
