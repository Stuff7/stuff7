from unittest import TestCase
from . import collections

class DictTest(TestCase):
  def test_safedict(self):
    sd = collections.SafeDict(a_key="Some key.", another_key="Some other key.")
    self.assertEqual(sd["a_key"], "Some key.")
    self.assertEqual(sd["another_key"], "Some other key.")
    self.assertEqual(sd["Some invalid key."], "{Some invalid key.}")
    self.assertEqual(sd[12], "{12}")
    self.assertIsNone(sd.get("Some other invalid key."))

  def test_pluraldict(self):
    pd = collections.PluralDict(zero= 0, plural= 12, singular= 1)
    self.assertEqual(pd["some invalid key"], "{some invalid key}")
    self.assertIsNone(pd.get("Some other invalid key."))
    self.assertEqual(pd["zero()"], "")
    self.assertEqual(pd["zero(some plural word)"], "some plural word")
    self.assertEqual(pd["zero(some singular word,)"], "")
    self.assertEqual(pd["plural(some plural word)"], "some plural word")
    self.assertEqual(pd["plural(some singular word,)"], "")
    self.assertEqual(pd["plural(this is, some plural word, the, rest, doesn't, matter)"], "some plural word")
    self.assertEqual(pd["singular(some singular word,)"], "some singular word")
    self.assertEqual(pd["singular(some plural word)"], "")
    self.assertEqual(pd["singular(some singular word, and, a bunch, of, nonsense)"], "some singular word")

  def test_safeformat(self):
    self.assertEqual(collections.safeformat((
      "My safe word is {safe_word} "
      "and here's an {unknown_word}"), safe_word="pickles"), (
      "My safe word is pickles "
      "and here's an {unknown_word}"
    ))
