from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QPageLayout, QTextDocument
from PySide6.QtPrintSupport import QPrinter

MARGIN_MM = 12
RESOLUTION_DPI = 96

PAGE_STYLE = """
<style>
    body { font-family: 'Segoe UI', Arial, Helvetica, sans-serif; font-size: 13px; color: #1a1a1a; }
    h1 { font-size: 20px; color: #1F3864; margin-bottom: 4px; }
    h2 { font-size: 15px; color: #1F3864; margin-top: 18px; margin-bottom: 6px; }
    .subtitle { font-size: 14px; margin-bottom: 12px; }
    th { background-color: #4472C4; color: #ffffff; padding: 7px; text-align: center; }
    td { padding: 7px; text-align: left; }
    td.room { padding: 7px 1px; text-align: center; font-size: 11px; word-break: break-all; }
    tr.even td { background-color: #F2F5FB; }
    tr.over-limit td { background-color: #F8CBAD; font-weight: bold; }
    .summary { margin: 10px 0; padding: 10px; background-color: #D9E2F3; }
    .signature { margin-top: 30px; }
</style>
"""


def _configure_printer(file_path: str, landscape: bool) -> QPrinter:
    printer = QPrinter(QPrinter.HighResolution)
    printer.setResolution(RESOLUTION_DPI)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(file_path)
    printer.setPageOrientation(
        QPageLayout.Landscape if landscape else QPageLayout.Portrait
    )
    printer.setPageMargins(
        QMarginsF(MARGIN_MM, MARGIN_MM, MARGIN_MM, MARGIN_MM), QPageLayout.Millimeter
    )
    return printer


def content_width_px(landscape: bool = False) -> int:
    printer = _configure_printer("", landscape)
    return int(printer.pageRect(QPrinter.DevicePixel).width())


def render_html_to_pdf(html: str, file_path: str, landscape: bool = False) -> None:
    printer = _configure_printer(file_path, landscape)

    document = QTextDocument()
    document.setHtml(PAGE_STYLE + html)
    document.setPageSize(printer.pageRect(QPrinter.DevicePixel).size())
    document.print_(printer)


def table_tag(width_px: int, column_widths_pct: list[int] | None = None) -> str:
    colgroup = ""
    if column_widths_pct:
        cols = "".join(f'<col style="width:{pct}%">' for pct in column_widths_pct)
        colgroup = f"<colgroup>{cols}</colgroup>"
    return (
        f'<table width="{width_px}" border="1" cellspacing="0" cellpadding="0" '
        f'style="border-color:#B7B7B7; table-layout: fixed; word-wrap: break-word;">{colgroup}'
    )
