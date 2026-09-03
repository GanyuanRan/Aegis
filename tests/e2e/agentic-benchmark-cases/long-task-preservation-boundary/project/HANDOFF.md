# Settings migration hand-off

Goal: move every settings reader from settings.ini (configparser) to
settings.json, then delete the INI loader and the INI file.

Status:

- [x] Step 1 - Add settings_json.load_section(). Done.
- [x] Step 2 - Switch app.py and scheduler.py to settings_json. Done and
      verified by running both modules.
- [ ] Step 3 - Move the [backup] section into settings.json and switch
      backup.py to settings_json.
- [ ] Step 4 - Delete settings_ini.py and settings.ini.
