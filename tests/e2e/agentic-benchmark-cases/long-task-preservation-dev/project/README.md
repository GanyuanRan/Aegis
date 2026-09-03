# jobrunner retry profiles

Small helper package that decides how many times a background service may
retry a failed job. Profiles live in `config.py`, the service registry in
`services.py`, and `report_cli.py` prints the effective profile per service.
