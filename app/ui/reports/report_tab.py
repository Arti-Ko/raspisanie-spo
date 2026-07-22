from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.export.excel_report import export_teacher_report as export_report_excel
from app.export.pdf_report import export_teacher_report as export_report_pdf
from app.repositories.reports import build_teacher_report
from app.repositories.teachers import list_teachers

WEEKLY_COLUMNS = ["Полугодие", "Неделя", "Группа", "Предмет", "Часов", "Замена"]
SUB_COLUMNS = ["Полугодие", "Неделя", "Группа", "Предмет", "Часов", "Кто"]


class ReportTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.teacher_combo = QComboBox()
        self.teacher_combo.currentIndexChanged.connect(self._on_teacher_changed)

        excel_button = QPushButton("Экспорт в Excel")
        excel_button.clicked.connect(self._on_export_excel)
        pdf_button = QPushButton("Экспорт в PDF")
        pdf_button.clicked.connect(self._on_export_pdf)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Преподаватель:"))
        selector_row.addWidget(self.teacher_combo)
        selector_row.addStretch()
        selector_row.addWidget(excel_button)
        selector_row.addWidget(pdf_button)

        self.summary_label = QLabel("")
        self._current_report = None

        self.weekly_table = QTableWidget(0, len(WEEKLY_COLUMNS))
        self.weekly_table.setHorizontalHeaderLabels(WEEKLY_COLUMNS)
        self.weekly_table.setAlternatingRowColors(True)
        self.weekly_table.horizontalHeader().setStretchLastSection(True)
        self.weekly_table.verticalHeader().setVisible(False)

        self.covered_by_others_table = QTableWidget(0, len(SUB_COLUMNS))
        self.covered_by_others_table.setHorizontalHeaderLabels(SUB_COLUMNS)
        self.covered_by_others_table.setAlternatingRowColors(True)
        self.covered_by_others_table.horizontalHeader().setStretchLastSection(True)
        self.covered_by_others_table.verticalHeader().setVisible(False)
        covered_by_others_box = QGroupBox("Кто заменял этого преподавателя")
        box_layout = QVBoxLayout(covered_by_others_box)
        box_layout.addWidget(self.covered_by_others_table)

        self.covered_for_others_table = QTableWidget(0, len(SUB_COLUMNS))
        self.covered_for_others_table.setHorizontalHeaderLabels(SUB_COLUMNS)
        self.covered_for_others_table.setAlternatingRowColors(True)
        self.covered_for_others_table.horizontalHeader().setStretchLastSection(True)
        self.covered_for_others_table.verticalHeader().setVisible(False)
        covered_for_others_box = QGroupBox("Кого заменял этот преподаватель")
        box_layout2 = QVBoxLayout(covered_for_others_box)
        box_layout2.addWidget(self.covered_for_others_table)

        substitutions_row = QHBoxLayout()
        substitutions_row.addWidget(covered_by_others_box)
        substitutions_row.addWidget(covered_for_others_box)

        layout = QVBoxLayout(self)
        layout.addLayout(selector_row)
        layout.addWidget(self.summary_label)
        layout.addWidget(QLabel("Помесячная / понедельная разбивка прочитанных часов:"))
        layout.addWidget(self.weekly_table)
        layout.addLayout(substitutions_row)

        self.refresh_reference_data()

    def refresh_reference_data(self) -> None:
        current_id = self.teacher_combo.currentData()
        self.teacher_combo.blockSignals(True)
        self.teacher_combo.clear()
        for teacher in list_teachers():
            self.teacher_combo.addItem(teacher.full_name, teacher.id)
        self.teacher_combo.blockSignals(False)
        index = self.teacher_combo.findData(current_id)
        self.teacher_combo.setCurrentIndex(index if index >= 0 else 0)
        self.refresh()

    def refresh(self) -> None:
        teacher_id = self.teacher_combo.currentData()
        if teacher_id is None:
            self.summary_label.setText("")
            self.weekly_table.setRowCount(0)
            self.covered_by_others_table.setRowCount(0)
            self.covered_for_others_table.setRowCount(0)
            self._current_report = None
            return

        report = build_teacher_report(teacher_id, self.teacher_combo.currentText())
        self._current_report = report

        self.summary_label.setText(
            f"По тарификации: I — {report.plan_hours[1]} ч., II — {report.plan_hours[2]} ч., всего {report.plan_total} ч.\n"
            f"Прочитано фактически: I — {report.actual_hours[1]} ч., II — {report.actual_hours[2]} ч., всего {report.actual_total} ч.\n"
            f"Разница (план − факт): {report.difference} ч."
        )

        self.weekly_table.setRowCount(len(report.weekly_lines))
        for row, line in enumerate(report.weekly_lines):
            self.weekly_table.setItem(row, 0, QTableWidgetItem(f"{line.semester}-е"))
            self.weekly_table.setItem(row, 1, QTableWidgetItem(str(line.week_number)))
            self.weekly_table.setItem(row, 2, QTableWidgetItem(line.group_name))
            self.weekly_table.setItem(row, 3, QTableWidgetItem(line.subject_name))
            self.weekly_table.setItem(row, 4, QTableWidgetItem(str(line.hours)))
            self.weekly_table.setItem(
                row, 5, QTableWidgetItem("да" if line.is_substitute else "")
            )
        self.weekly_table.resizeColumnsToContents()

        self._fill_substitution_table(
            self.covered_by_others_table, report.covered_by_others
        )
        self._fill_substitution_table(
            self.covered_for_others_table, report.covered_for_others
        )

    def _on_teacher_changed(self, _index: int) -> None:
        self.refresh()

    def _on_export_excel(self) -> None:
        if not self._require_report():
            return
        default_name = f"Справка_{self._current_report.teacher_name}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в Excel", default_name, "Excel (*.xlsx)"
        )
        if not file_path:
            return
        try:
            export_report_excel(self._current_report, file_path)
        except OSError as error:
            QMessageBox.warning(self, "Ошибка экспорта", str(error))
            return
        QMessageBox.information(
            self, "Экспорт завершён", f"Файл сохранён:\n{file_path}"
        )

    def _on_export_pdf(self) -> None:
        if not self._require_report():
            return
        default_name = f"Справка_{self._current_report.teacher_name}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в PDF", default_name, "PDF (*.pdf)"
        )
        if not file_path:
            return
        try:
            export_report_pdf(self._current_report, file_path)
        except OSError as error:
            QMessageBox.warning(self, "Ошибка экспорта", str(error))
            return
        QMessageBox.information(
            self, "Экспорт завершён", f"Файл сохранён:\n{file_path}"
        )

    def _require_report(self) -> bool:
        if self._current_report is None:
            QMessageBox.information(self, "Экспорт", "Сначала выберите преподавателя.")
            return False
        return True

    @staticmethod
    def _fill_substitution_table(table: QTableWidget, lines) -> None:
        table.setRowCount(len(lines))
        for row, line in enumerate(lines):
            table.setItem(row, 0, QTableWidgetItem(f"{line.semester}-е"))
            table.setItem(row, 1, QTableWidgetItem(str(line.week_number)))
            table.setItem(row, 2, QTableWidgetItem(line.group_name))
            table.setItem(row, 3, QTableWidgetItem(line.subject_name))
            table.setItem(row, 4, QTableWidgetItem(str(line.hours)))
            table.setItem(row, 5, QTableWidgetItem(line.other_teacher_name))
        table.resizeColumnsToContents()
