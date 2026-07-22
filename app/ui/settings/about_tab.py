from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from app.repositories.update_check import check_for_update
from app.version import __version__


class AboutTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.version_label = QLabel(f"Текущая версия: {__version__}")
        self.status_label = QLabel("")

        check_button = QPushButton("Проверить обновления")
        check_button.clicked.connect(self._on_check)

        self.download_button = QPushButton("Скачать новую версию")
        self.download_button.setVisible(False)
        self.download_button.clicked.connect(self._on_download)
        self._release_url: str | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(self.version_label)
        layout.addWidget(check_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.download_button)
        layout.addStretch()

    def _on_check(self) -> None:
        result = check_for_update()
        self.download_button.setVisible(False)
        if result.error:
            self.status_label.setText(
                "Не удалось проверить обновления (нет сети или GitHub недоступен)."
            )
            return
        if result.update_available:
            self.status_label.setText(f"Доступна новая версия: {result.latest_version}")
            self._release_url = result.release_url
            self.download_button.setVisible(True)
        else:
            self.status_label.setText("У вас установлена последняя версия.")

    def _on_download(self) -> None:
        if self._release_url:
            QDesktopServices.openUrl(QUrl(self._release_url))
