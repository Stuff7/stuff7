class SafeDict(dict):
  """ For any missing key it will return {key}
  Useful for the str.format_map function when
  working with arbitrary string and you don't
  know if all the values will be present. """
  def __missing__(self, key):
    return f"{{{key}}}"

class PluralDict(dict):
  """ Parses keys with the form "key(singular, plural)"
  and also "key(plural)".
  If the value in the key is 1 it returns singular
  for everything else it returns plural """
  def __missing__(self, key):
    if "(" in key and key.endswith(")"):
      key, rest = key.split("(", 1)
      value = super().__getitem__(key)
      suffix = rest.rstrip(")").split(",")
      if len(suffix) == 1:
        suffix.insert(0, "")
      return suffix[0].strip() if value == 1 else suffix[1].strip()
    return f"{{{key}}}"

def safeformat(string, **options):
  """ Formatting and ignoring missing keys in strings. """
  try:
    return string.format_map(SafeDict(options))
  except ValueError as e:
    return f"There was a parsing error: {e}"
