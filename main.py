import sys

from PySide6.QtWidgets import QApplication

from app.db.database import init_db
from app.repositories.auth import ensure_default_password
from app.ui.login_dialog import LoginDialog
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme


def main() -> None:
    init_db()
    ensure_default_password()
    app = QApplication(sys.argv)
    apply_theme(app)

    if not LoginDialog().exec():
        sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
