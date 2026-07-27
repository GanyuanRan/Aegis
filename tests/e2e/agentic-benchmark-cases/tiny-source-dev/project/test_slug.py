from slug import is_valid_slug


assert is_valid_slug("release-notes") is True
assert is_valid_slug("   ") is False
