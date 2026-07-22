from PySide6.QtWidgets import QMainWindow, QTabWidget

from app.ui.reports.report_tab import ReportTab
from app.ui.schedule.schedule_tab import ScheduleTab
from app.ui.settings.settings_tab import SettingsTab
from app.ui.tarification.tarification_tab import TarificationTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тарификация и расписание")
        self.resize(1100, 700)

        self.tarification_tab = TarificationTab()
        self.schedule_tab = ScheduleTab()
        self.report_tab = ReportTab()

        tabs = QTabWidget()
        tabs.addTab(self.tarification_tab, "Тарификация")
        tabs.addTab(self.schedule_tab, "Расписание")
        tabs.addTab(self.report_tab, "Отчёты")
        tabs.addTab(SettingsTab(), "Настройки")
        tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(tabs)

    def _on_tab_changed(self, index: int) -> None:
        widget = self.centralWidget().widget(index)
        if hasattr(widget, "refresh_reference_data"):
            widget.refresh_reference_data()
