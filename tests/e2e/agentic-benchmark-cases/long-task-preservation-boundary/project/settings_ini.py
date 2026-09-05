"""Legacy INI settings loader (scheduled for removal)."""

import configparser
from pathlib import Path

INI_PATH = Path(__file__).with_name("settings.ini")


def load_ini(section):
    parser = configparser.ConfigParser()
    parser.read(INI_PATH)
    return dict(parser[section])
