import unittest
from validators import is_valid_email

class EmailTest(unittest.TestCase):
    def test_plain(self): self.assertTrue(is_valid_email('a@example.com'))
    def test_dotted(self): self.assertTrue(is_valid_email('a.b@example.com'))
    def test_hyphen(self): self.assertTrue(is_valid_email('a-b@example.com'))
    def test_invalid(self): self.assertFalse(is_valid_email('not-an-email'))
    def test_plus_tag(self): self.assertTrue(is_valid_email('a+tag@example.com'))

if __name__ == '__main__': unittest.main()
