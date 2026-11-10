"""Styled message dialogs that stay readable in light and dark themes."""

from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QWidget

from app.ui.theme import Theme


def _is_dark(parent: QWidget | None) -> bool:
    window = parent.window() if parent is not None else None
    return bool(getattr(window, "_is_dark", False))


def _box(parent: QWidget | None) -> QMessageBox:
    box = QMessageBox(parent)
    # Applying a stylesheet forces the Qt dialog on macOS instead of the native alert,
    # which avoids unreadable system-dark text colors.
    box.setStyleSheet(Theme.message_box_stylesheet(_is_dark(parent)))
    return box


def information(parent: QWidget | None, title: str, text: str) -> None:
    box = _box(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()


def success(parent: QWidget | None, title: str, text: str) -> None:
    """Completion notification after Excel generation or PDF conversion."""
    information(parent, title, text)


def warning(parent: QWidget | None, title: str, text: str) -> None:
    box = _box(parent)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()


def critical(parent: QWidget | None, title: str, text: str) -> None:
    box = _box(parent)
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()


def question(parent: QWidget | None, title: str, text: str) -> bool:
    box = _box(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    box.setDefaultButton(QMessageBox.StandardButton.No)
    return box.exec() == QMessageBox.StandardButton.Yes
