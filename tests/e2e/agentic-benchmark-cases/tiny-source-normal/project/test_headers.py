from headers import is_safe_header_value


assert is_safe_header_value("text/plain") is True
assert is_safe_header_value("ok\r\nX-Injected: yes") is False
assert is_safe_header_value("ok\nX-Injected: yes") is False
