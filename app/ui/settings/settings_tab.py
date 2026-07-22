from PySide6.QtWidgets import QTabWidget

from app.ui.settings.about_tab import AboutTab
from app.ui.settings.bell_times_tab import BellTimesTab
from app.ui.settings.calendar_tab import CalendarTab
from app.ui.settings.curriculum_tab import CurriculumTab
from app.ui.settings.groups_tab import GroupsTab
from app.ui.settings.password_tab import PasswordTab
from app.ui.settings.programs_tab import ProgramsTab
from app.ui.settings.teachers_tab import TeachersTab


class SettingsTab(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.teachers_tab = TeachersTab()
        self.programs_tab = ProgramsTab()
        self.groups_tab = GroupsTab()
        self.calendar_tab = CalendarTab()
        self.curriculum_tab = CurriculumTab()
        self.bell_times_tab = BellTimesTab()
        self.password_tab = PasswordTab()
        self.about_tab = AboutTab()

        self.addTab(self.teachers_tab, "Преподаватели")
        self.addTab(self.programs_tab, "Программы")
        self.addTab(self.groups_tab, "Группы")
        self.addTab(self.calendar_tab, "Календарь")
        self.addTab(self.curriculum_tab, "Учебный план")
        self.addTab(self.bell_times_tab, "Звонки")
        self.addTab(self.password_tab, "Пароль")
        self.addTab(self.about_tab, "О программе")

        self.currentChanged.connect(self._on_tab_changed)

    def refresh_reference_data(self) -> None:
        self._on_tab_changed(self.currentIndex())

    def _on_tab_changed(self, index: int) -> None:
        widget = self.widget(index)
        if hasattr(widget, "refresh_reference_data"):
            widget.refresh_reference_data()
        elif hasattr(widget, "refresh"):
            widget.refresh()
