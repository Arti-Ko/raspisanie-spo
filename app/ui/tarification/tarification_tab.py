from PySide6.QtWidgets import QTabWidget

from app.ui.tarification.group_assignments_widget import GroupAssignmentsWidget
from app.ui.tarification.teacher_summary_widget import TeacherSummaryWidget


class TarificationTab(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.group_assignments = GroupAssignmentsWidget()
        self.teacher_summary = TeacherSummaryWidget()

        self.addTab(self.group_assignments, "Назначения")
        self.addTab(self.teacher_summary, "Сводка по преподавателям")

        self.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int) -> None:
        widget = self.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def refresh_reference_data(self) -> None:
        self.group_assignments.reload_groups()
        self.teacher_summary.reload_years()
