"""About View [qslots]
Author(s): Jason C. McDonald

Displays "about" data for qslots.
"""

import os
from pathlib import Path
from pkg_resources import resource_filename

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class AboutView:
    widget = QWidget()
    layout = QVBoxLayout()
    lbl_info = QTextEdit()

    @classmethod
    def build(cls):
        """Build the interface."""
        cls.lbl_info = QTextEdit()

        about_path = resource_filename(
            'qslots',
            os.path.join('resources', 'about.txt')
        )
        about_file = Path(about_path)
        try:
            with about_file.open('r', encoding='utf-8') as file:
                cls.lbl_info.setPlainText(file.read())
        except FileNotFoundError:
            cls.lbl_info.setPlainText("qslots\n"
                                      "Created by Jason C. McDonald\n\n"
                                      "ERROR: `resources/about.txt` missing")
        cls.lbl_info.setWhatsThis("Credits and license for qslots.")
        cls.lbl_info.setReadOnly(True)
        cls.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cls.widget.setLayout(cls.layout)
        cls.layout.addWidget(cls.lbl_info)

        return cls.widget
