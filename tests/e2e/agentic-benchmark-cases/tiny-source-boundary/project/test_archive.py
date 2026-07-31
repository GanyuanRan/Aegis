from archive import is_safe_archive_name


assert is_safe_archive_name("exports/july.zip") is True
assert is_safe_archive_name("../secrets.zip") is False
assert is_safe_archive_name("exports/../../secrets.zip") is False
