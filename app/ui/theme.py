"""Application color palette and light/dark stylesheets."""

from __future__ import annotations


class Theme:
    """Central place for Report Studio visual tokens."""

    PRIMARY = "#356DE0"
    PRIMARY_HOVER = "#2B5BC4"
    SIDEBAR = "#F1F4F9"
    BACKGROUND = "#FFFFFF"
    HEADING = "#17243A"
    SECONDARY_TEXT = "#6B7A90"
    BORDER = "#E2E8F0"
    SUCCESS = "#22A06B"
    SUCCESS_BG = "#E8F8F0"
    ERROR = "#E5484D"
    CARD_SHADOW = "rgba(23, 36, 58, 0.06)"

    # Dark theme overrides
    DARK_BACKGROUND = "#121826"
    DARK_SIDEBAR = "#1A2233"
    DARK_CARD = "#1E2838"
    DARK_HEADING = "#F5F7FB"
    DARK_SECONDARY = "#9AA8BC"
    DARK_BORDER = "#2C3A4F"

    @classmethod
    def message_box_stylesheet(cls, dark: bool = False) -> str:
        """Standalone styles that force readable Qt dialogs (including on macOS)."""
        if dark:
            background = cls.DARK_CARD
            text = cls.DARK_HEADING
        else:
            background = cls.BACKGROUND
            text = cls.HEADING

        return f"""
        QMessageBox {{
            background-color: {background};
            color: {text};
        }}
        QMessageBox QLabel {{
            color: {text};
            background-color: transparent;
            font-size: 13px;
        }}
        QMessageBox QPushButton {{
            background-color: {cls.PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            min-width: 72px;
            font-weight: 600;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {cls.PRIMARY_HOVER};
        }}
        QMessageBox QPushButton:default {{
            background-color: {cls.PRIMARY};
            color: white;
        }}
        """

    @classmethod
    def progress_dialog_stylesheet(cls, dark: bool = False) -> str:
        """Styles for the modal progress dialog and animated progress bar."""
        if dark:
            background = cls.DARK_CARD
            title = cls.DARK_HEADING
            message = cls.DARK_SECONDARY
            track = cls.DARK_BORDER
        else:
            background = cls.BACKGROUND
            title = cls.HEADING
            message = cls.SECONDARY_TEXT
            track = cls.BORDER

        return f"""
        QDialog#progressDialog {{
            background-color: {background};
        }}
        QLabel#progressTitle {{
            color: {title};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
        }}
        QLabel#progressMessage {{
            color: {message};
            font-size: 13px;
            background: transparent;
        }}
        QProgressBar#progressBar {{
            background-color: {track};
            border: none;
            border-radius: 7px;
            min-height: 14px;
            max-height: 14px;
            text-align: center;
        }}
        QProgressBar#progressBar::chunk {{
            background-color: {cls.PRIMARY};
            border-radius: 7px;
        }}
        """

    @classmethod
    def light_stylesheet(cls) -> str:
        return f"""
        QWidget {{
            font-family: "Helvetica Neue", Helvetica, Arial;
            font-size: 13px;
            color: {cls.HEADING};
        }}

        QMainWindow, #centralRoot {{
            background-color: {cls.BACKGROUND};
        }}

        #sidebar {{
            background-color: {cls.SIDEBAR};
            border-right: 1px solid {cls.BORDER};
        }}

        #brandTitle {{
            font-size: 16px;
            font-weight: 700;
            color: {cls.HEADING};
        }}

        #brandSubtitle {{
            font-size: 11px;
            color: {cls.SECONDARY_TEXT};
        }}

        QPushButton#navButton {{
            text-align: left;
            padding: 10px 14px;
            border: none;
            border-radius: 10px;
            color: {cls.HEADING};
            background: transparent;
            font-weight: 500;
        }}

        QPushButton#navButton:hover {{
            background-color: #E4EAF3;
        }}

        QPushButton#navButton[active="true"] {{
            background-color: {cls.PRIMARY};
            color: white;
            font-weight: 600;
        }}

        #contentArea {{
            background-color: {cls.BACKGROUND};
        }}

        #pageTitle {{
            font-size: 28px;
            font-weight: 700;
            color: {cls.HEADING};
        }}

        #pageSubtitle {{
            font-size: 13px;
            color: {cls.SECONDARY_TEXT};
        }}

        #statCard, #activityCard, #placeholderCard, #formCard, #tableCard {{
            background-color: {cls.BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: 14px;
        }}

        #statCard[clickable="true"]:hover {{
            border-color: {cls.PRIMARY};
        }}

        #statValue {{
            font-size: 34px;
            font-weight: 700;
            color: {cls.HEADING};
        }}

        #statLabel {{
            font-size: 15px;
            font-weight: 600;
            color: {cls.HEADING};
        }}

        #statHint {{
            font-size: 12px;
            color: {cls.SECONDARY_TEXT};
        }}

        #sectionTitle {{
            font-size: 16px;
            font-weight: 700;
            color: {cls.HEADING};
        }}

        QPushButton#primaryButton {{
            background-color: {cls.PRIMARY};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 18px;
            font-weight: 600;
        }}

        QPushButton#primaryButton:hover {{
            background-color: {cls.PRIMARY_HOVER};
        }}

        QPushButton#secondaryButton {{
            background-color: {cls.BACKGROUND};
            color: {cls.HEADING};
            border: 1px solid {cls.BORDER};
            border-radius: 10px;
            padding: 10px 18px;
            font-weight: 600;
        }}

        QPushButton#secondaryButton:hover {{
            border-color: {cls.PRIMARY};
            color: {cls.PRIMARY};
        }}

        QPushButton#linkButton {{
            background: transparent;
            border: none;
            color: {cls.PRIMARY};
            font-weight: 600;
            padding: 4px 8px;
        }}

        QPushButton#linkButton:hover {{
            color: {cls.PRIMARY_HOVER};
        }}

        QPushButton#themeToggle {{
            background-color: {cls.SIDEBAR};
            border: 1px solid {cls.BORDER};
            border-radius: 10px;
            padding: 8px 12px;
            min-width: 84px;
        }}

        QPushButton#themeToggle:hover {{
            border-color: {cls.PRIMARY};
        }}

        QPushButton#iconButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 4px 8px;
            min-width: 32px;
            color: {cls.SECONDARY_TEXT};
            font-size: 14px;
        }}

        QPushButton#iconButton:hover {{
            background-color: {cls.SIDEBAR};
            border-color: {cls.BORDER};
            color: {cls.PRIMARY};
        }}

        QPushButton#iconButton[danger="true"]:hover {{
            color: {cls.ERROR};
            border-color: #F5C2C2;
            background-color: #FDECEC;
        }}

        QLabel#fieldLabel {{
            font-size: 12px;
            font-weight: 600;
            color: {cls.SECONDARY_TEXT};
        }}

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {cls.BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: 10px;
            padding: 8px 12px;
            min-height: 20px;
            color: {cls.HEADING};
            selection-background-color: #EEF3FC;
            selection-color: {cls.HEADING};
        }}

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {cls.PRIMARY};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {cls.BACKGROUND};
            color: {cls.HEADING};
            border: 1px solid {cls.BORDER};
            border-radius: 8px;
            outline: 0;
            padding: 4px;
            selection-background-color: #EEF3FC;
            selection-color: {cls.HEADING};
        }}

        QComboBox QAbstractItemView::item {{
            color: {cls.HEADING};
            background-color: {cls.BACKGROUND};
            padding: 8px 10px;
            min-height: 24px;
        }}

        QComboBox QAbstractItemView::item:selected {{
            background-color: #EEF3FC;
            color: {cls.HEADING};
        }}

        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            width: 0px;
            border: none;
        }}

        QSpinBox::up-arrow, QSpinBox::down-arrow,
        QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {{
            width: 0px;
            height: 0px;
        }}

        QLineEdit#searchInput {{
            padding-left: 14px;
            min-height: 22px;
        }}

        QTableWidget#activityTable, QTableWidget#recordsTable, QTableWidget#reportsTable {{
            background: transparent;
            border: none;
            gridline-color: {cls.BORDER};
            selection-background-color: #EEF3FC;
            selection-color: {cls.HEADING};
        }}

        QTableWidget#activityTable::item, QTableWidget#recordsTable::item, QTableWidget#reportsTable::item {{
            padding: 8px;
            border-bottom: 1px solid {cls.BORDER};
        }}

        QHeaderView::section {{
            background-color: transparent;
            border: none;
            border-bottom: 1px solid {cls.BORDER};
            color: {cls.SECONDARY_TEXT};
            font-weight: 600;
            padding: 10px 8px;
        }}

        #grandTotalValue {{
            color: {cls.SUCCESS};
            font-weight: 700;
        }}

        QScrollArea {{
            border: none;
            background: transparent;
        }}

        QScrollArea#excelSelectList {{
            background-color: {cls.SIDEBAR};
            border: 1px solid {cls.BORDER};
            border-radius: 12px;
        }}

        QScrollArea#excelSelectList > QWidget > QWidget {{
            background-color: {cls.SIDEBAR};
        }}

        #excelSelectContainer {{
            background-color: {cls.SIDEBAR};
        }}

        QFrame#excelSelectRow {{
            background-color: {cls.BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: 10px;
        }}

        QFrame#excelSelectRow[selected="true"] {{
            background-color: #EEF3FC;
            border: 1px solid {cls.PRIMARY};
        }}

        QLabel#excelSelectName {{
            color: {cls.HEADING};
            font-weight: 600;
            font-size: 13px;
            background: transparent;
        }}

        QLabel#excelSelectDate {{
            color: {cls.SECONDARY_TEXT};
            font-size: 11px;
            background: transparent;
        }}

        QRadioButton#excelSelectRadio {{
            color: {cls.HEADING};
            background: transparent;
            spacing: 8px;
        }}
        """ + cls.message_box_stylesheet(dark=False)

    @classmethod
    def dark_stylesheet(cls) -> str:
        return f"""
        QWidget {{
            font-family: "Helvetica Neue", Helvetica, Arial;
            font-size: 13px;
            color: {cls.DARK_HEADING};
        }}

        QMainWindow, #centralRoot {{
            background-color: {cls.DARK_BACKGROUND};
        }}

        #sidebar {{
            background-color: {cls.DARK_SIDEBAR};
            border-right: 1px solid {cls.DARK_BORDER};
        }}

        #brandTitle {{
            font-size: 16px;
            font-weight: 700;
            color: {cls.DARK_HEADING};
        }}

        #brandSubtitle {{
            font-size: 11px;
            color: {cls.DARK_SECONDARY};
        }}

        QPushButton#navButton {{
            text-align: left;
            padding: 10px 14px;
            border: none;
            border-radius: 10px;
            color: {cls.DARK_HEADING};
            background: transparent;
            font-weight: 500;
        }}

        QPushButton#navButton:hover {{
            background-color: #243044;
        }}

        QPushButton#navButton[active="true"] {{
            background-color: {cls.PRIMARY};
            color: white;
            font-weight: 600;
        }}

        #contentArea {{
            background-color: {cls.DARK_BACKGROUND};
        }}

        #pageTitle {{
            font-size: 28px;
            font-weight: 700;
            color: {cls.DARK_HEADING};
        }}

        #pageSubtitle {{
            font-size: 13px;
            color: {cls.DARK_SECONDARY};
        }}

        #statCard, #activityCard, #placeholderCard, #formCard, #tableCard {{
            background-color: {cls.DARK_CARD};
            border: 1px solid {cls.DARK_BORDER};
            border-radius: 14px;
        }}

        #statCard[clickable="true"]:hover {{
            border-color: {cls.PRIMARY};
        }}

        #statValue {{
            font-size: 34px;
            font-weight: 700;
            color: {cls.DARK_HEADING};
        }}

        #statLabel {{
            font-size: 15px;
            font-weight: 600;
            color: {cls.DARK_HEADING};
        }}

        #statHint {{
            font-size: 12px;
            color: {cls.DARK_SECONDARY};
        }}

        #sectionTitle {{
            font-size: 16px;
            font-weight: 700;
            color: {cls.DARK_HEADING};
        }}

        QPushButton#primaryButton {{
            background-color: {cls.PRIMARY};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 18px;
            font-weight: 600;
        }}

        QPushButton#primaryButton:hover {{
            background-color: {cls.PRIMARY_HOVER};
        }}

        QPushButton#secondaryButton {{
            background-color: {cls.DARK_CARD};
            color: {cls.DARK_HEADING};
            border: 1px solid {cls.DARK_BORDER};
            border-radius: 10px;
            padding: 10px 18px;
            font-weight: 600;
        }}

        QPushButton#secondaryButton:hover {{
            border-color: {cls.PRIMARY};
            color: #7BA3F0;
        }}

        QPushButton#linkButton {{
            background: transparent;
            border: none;
            color: #7BA3F0;
            font-weight: 600;
            padding: 4px 8px;
        }}

        QPushButton#themeToggle {{
            background-color: {cls.DARK_CARD};
            border: 1px solid {cls.DARK_BORDER};
            border-radius: 10px;
            padding: 8px 12px;
            min-width: 84px;
            color: {cls.DARK_HEADING};
        }}

        QPushButton#iconButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 4px 8px;
            min-width: 32px;
            color: {cls.DARK_SECONDARY};
            font-size: 14px;
        }}

        QPushButton#iconButton:hover {{
            background-color: #243044;
            border-color: {cls.DARK_BORDER};
            color: #7BA3F0;
        }}

        QPushButton#iconButton[danger="true"]:hover {{
            color: {cls.ERROR};
            border-color: #7A3030;
            background-color: #3A1F24;
        }}

        QLabel#fieldLabel {{
            font-size: 12px;
            font-weight: 600;
            color: {cls.DARK_SECONDARY};
        }}

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {cls.DARK_BACKGROUND};
            border: 1px solid {cls.DARK_BORDER};
            border-radius: 10px;
            padding: 8px 12px;
            min-height: 20px;
            color: {cls.DARK_HEADING};
            selection-background-color: #243044;
            selection-color: {cls.DARK_HEADING};
        }}

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {cls.PRIMARY};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {cls.DARK_CARD};
            color: {cls.DARK_HEADING};
            border: 1px solid {cls.DARK_BORDER};
            border-radius: 8px;
            outline: 0;
            padding: 4px;
            selection-background-color: #243044;
            selection-color: {cls.DARK_HEADING};
        }}

        QComboBox QAbstractItemView::item {{
            color: {cls.DARK_HEADING};
            background-color: {cls.DARK_CARD};
            padding: 8px 10px;
            min-height: 24px;
        }}

        QComboBox QAbstractItemView::item:selected {{
            background-color: #243044;
            color: {cls.DARK_HEADING};
        }}

        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            width: 0px;
            border: none;
        }}

        QSpinBox::up-arrow, QSpinBox::down-arrow,
        QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {{
            width: 0px;
            height: 0px;
        }}

        QLineEdit#searchInput {{
            padding-left: 14px;
            min-height: 22px;
        }}

        QTableWidget#activityTable, QTableWidget#recordsTable, QTableWidget#reportsTable {{
            background: transparent;
            border: none;
            gridline-color: {cls.DARK_BORDER};
            selection-background-color: #243044;
            selection-color: {cls.DARK_HEADING};
            color: {cls.DARK_HEADING};
        }}

        QTableWidget#activityTable::item, QTableWidget#recordsTable::item, QTableWidget#reportsTable::item {{
            padding: 8px;
            border-bottom: 1px solid {cls.DARK_BORDER};
        }}

        QHeaderView::section {{
            background-color: transparent;
            border: none;
            border-bottom: 1px solid {cls.DARK_BORDER};
            color: {cls.DARK_SECONDARY};
            font-weight: 600;
            padding: 10px 8px;
        }}

        #grandTotalValue {{
            color: {cls.SUCCESS};
            font-weight: 700;
        }}

        QScrollArea {{
            border: none;
            background: transparent;
        }}

        QScrollArea#excelSelectList {{
            background-color: {cls.DARK_BACKGROUND};
            border: 1px solid {cls.DARK_BORDER};
            border-radius: 12px;
        }}

        QScrollArea#excelSelectList > QWidget > QWidget {{
            background-color: {cls.DARK_BACKGROUND};
        }}

        #excelSelectContainer {{
            background-color: {cls.DARK_BACKGROUND};
        }}

        QFrame#excelSelectRow {{
            background-color: {cls.DARK_CARD};
            border: 1px solid {cls.DARK_BORDER};
            border-radius: 10px;
        }}

        QFrame#excelSelectRow[selected="true"] {{
            background-color: #243044;
            border: 1px solid {cls.PRIMARY};
        }}

        QLabel#excelSelectName {{
            color: {cls.DARK_HEADING};
            font-weight: 600;
            font-size: 13px;
            background: transparent;
        }}

        QLabel#excelSelectDate {{
            color: {cls.DARK_SECONDARY};
            font-size: 11px;
            background: transparent;
        }}

        QRadioButton#excelSelectRadio {{
            color: {cls.DARK_HEADING};
            background: transparent;
            spacing: 8px;
        }}
        """ + cls.message_box_stylesheet(dark=True)
