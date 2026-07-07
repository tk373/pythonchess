import os
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import QSettings
from stockfish import Stockfish

ORG_NAME = "ChessOpeningTrainer"
APP_NAME = "ChessOpeningTrainer"
SETTINGS_KEY = "stockfish_path"


def _prompt_for_stockfish_path(app):
    QMessageBox.information(
        None,
        "Stockfish Path Required",
        "No Stockfish binary has been configured yet.\n\n"
        "Please select the Stockfish executable on your system.",
    )

    path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Stockfish Binary",
        os.path.expanduser("~"),
    )
    return path


def get_stockfish_path():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    settings = QSettings(ORG_NAME, APP_NAME)
    path = settings.value(SETTINGS_KEY, "", type=str)

    while not path or not os.path.isfile(path):
        path = _prompt_for_stockfish_path(app)
        if not path:
            retry = QMessageBox.question(
                None,
                "No Path Selected",
                "A Stockfish binary is required to run this application.\n"
                "Do you want to try again?",
                QMessageBox.Retry | QMessageBox.Abort,
            )
            if retry == QMessageBox.Abort:
                sys.exit("Stockfish path was not configured. Exiting.")
            continue

        if not os.path.isfile(path):
            QMessageBox.warning(
                None,
                "Invalid Path",
                "The selected path does not point to a valid file. Please try again.",
            )
            path = ""

    settings.setValue(SETTINGS_KEY, path)
    return path


def get_stockfish_instance(skill_level):
    """Return a working Stockfish instance, reprompting for a path if the
    saved/selected binary turns out not to actually be Stockfish."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    settings = QSettings(ORG_NAME, APP_NAME)

    while True:
        path = get_stockfish_path()
        try:
            engine = Stockfish(path)
            engine.set_skill_level(skill_level)
            return engine
        except Exception as e:
            settings.remove(SETTINGS_KEY)
            QMessageBox.warning(
                None,
                "Invalid Stockfish Binary",
                f"Could not start Stockfish from the selected file:\n{path}\n\n"
                f"Error: {e}\n\nPlease select a valid Stockfish binary.",
            )
