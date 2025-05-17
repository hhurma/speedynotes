import os
import json
from helpers.config_helper import get_data_dir, set_data_dir
from gui.first_run_wizard import FirstRunWizard
from PyQt6.QtWidgets import QApplication

def ensure_config_files():
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)
    notes_path = os.path.join(data_dir, 'notes.json')
    settings_path = os.path.join(data_dir, 'settings.json')

    if not os.path.exists(notes_path):
        with open(notes_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    if not os.path.exists(settings_path):
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def run_first_time_wizard_if_needed():
    data_dir = get_data_dir()
    notes_path = os.path.join(data_dir, 'notes.json')
    settings_path = os.path.join(data_dir, 'settings.json')
    if not os.path.exists(notes_path) or not os.path.exists(settings_path) or data_dir == 'config':
        app = QApplication.instance() or QApplication([])
        wizard = FirstRunWizard()
        if wizard.exec() == 1 and wizard.get_selected_dir():
            set_data_dir(wizard.get_selected_dir())
            ensure_config_files()

run_first_time_wizard_if_needed()
ensure_config_files()

from gui.main_gui import main

if __name__ == "__main__":
    main() 