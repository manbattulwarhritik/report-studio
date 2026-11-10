"""Modal progress dialog with an animated indeterminate progress bar."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from app.ui.theme import Theme


class ProgressDialog(QDialog):
    """Shows animated progress while Excel generation or PDF conversion runs."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("progressDialog")
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )
        self.setMinimumWidth(380)
        self._build_ui()
        self.apply_theme(dark=False)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        self.title_label = QLabel("Working…")
        self.title_label.setObjectName("progressTitle")
        layout.addWidget(self.title_label)

        self.message_label = QLabel("Please wait.")
        self.message_label.setObjectName("progressMessage")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate animation
        self.progress_bar.setMinimumHeight(14)
        layout.addWidget(self.progress_bar)

    def apply_theme(self, dark: bool) -> None:
        self.setStyleSheet(Theme.progress_dialog_stylesheet(dark=dark))

    def show_progress(self, title: str, message: str) -> None:
        """Display the dialog with an animated indeterminate bar."""
        self.setWindowTitle(title)
        self.title_label.setText(title)
        self.message_label.setText(message)
        self.progress_bar.setRange(0, 0)
        self.setEnabled(True)
        self.show()
        self.raise_()
        self.activateWindow()

    def close_progress(self) -> None:
        """Stop animation and hide the dialog."""
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.hide()

    def reject(self) -> None:
        # Ignore Escape / close while a job is running.
        return

    def closeEvent(self, event) -> None:  # noqa: N802
        event.ignore()
