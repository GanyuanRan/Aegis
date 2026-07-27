def socket_path(config):
    return config.get("socket_path") or config.get("legacy_socket")
