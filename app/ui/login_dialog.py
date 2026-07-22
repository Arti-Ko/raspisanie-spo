from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from app.repositories.auth import verify_password


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход")
        self.setMinimumWidth(320)
        self.setModal(True)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #C0392B;")

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.returnPressed.connect(self._on_accept)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Введите пароль для доступа к программе:"))
        layout.addWidget(self.password_edit)
        layout.addWidget(self.error_label)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if verify_password(self.password_edit.text()):
            self.accept()
            return
        self.error_label.setText("Неверный пароль, попробуйте ещё раз.")
        self.password_edit.clear()
        self.password_edit.setFocus()
