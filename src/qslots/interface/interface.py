"""Interface [qslots]
Author(s): Jason C. McDonald

Top-level functions for the interface sub-package. These are the functions
initially called to build and run the interface.
"""

from qslots.interface.app import App
from qslots.interface.appcontrols import AppControls
from qslots.interface.focus import Focus
from qslots.interface.notes import Notes
from qslots.interface.timecontrols import TimeControls
from qslots.interface.timedisplay import TimeDisplay
from qslots.interface.systray import SysTray
from qslots.interface.workspace import Workspace

from qslots.data.backup import Backup

from qslots.logic.clock import Clock


def build():
    """Construct the interface."""
    # Build the actual interface.
    App.build()
    App.add_widget(TimeDisplay.build())
    App.add_widget(Notes.build())
    App.add_widget(TimeControls.build())
    App.add_widget(Workspace.build())
    App.add_widget(AppControls.build())
    SysTray.build()

    # See if there's anything to recover from a damaged session.
    Backup.check_for_recall()
    # Start monitoring new timers.
    Backup.start_monitoring()

    # Initialize systems
    Focus.initialize()

    # Start the clock!
    Clock.start()


def run():
    """Run the interface."""
    build()
    return App.run()
