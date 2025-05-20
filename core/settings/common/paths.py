from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SETTINGS_DIR = BASE_DIR / 'core' / 'settings'
COMMON_DIR = SETTINGS_DIR / 'common'
PRINTERS_DIR = BASE_DIR / 'printers'
TEMPLATES_DIR = BASE_DIR / 'templates'