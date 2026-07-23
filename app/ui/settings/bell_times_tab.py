from PySide6.QtWidgets import QTabWidget

from app.repositories.bell_times import DAY_NAMES
from app.ui.settings.day_bell_schedule_widget import DayBellScheduleWidget


class BellTimesTab(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.day_widgets: dict[int, DayBellScheduleWidget] = {}
        for day_of_week, name in DAY_NAMES.items():
            widget = DayBellScheduleWidget(day_of_week)
            self.day_widgets[day_of_week] = widget
            self.addTab(widget, name)

    def refresh_reference_data(self) -> None:
        for widget in self.day_widgets.values():
            widget.load()
