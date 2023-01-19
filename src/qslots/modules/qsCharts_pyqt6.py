import sys

from PyQt6 import (
    QtCore,
    QtWidgets,
)

# import PyQt6 before matplotlib

from PyQt6.QtGui import QPalette, QPixmap, QFont

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QBrush, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QLabel,
    QFrame,
)

import matplotlib
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import ticker
from matplotlib.widgets import Slider, Button

from dataclasses import dataclass
from typing import Any

import qsPlot_PyQt as qsp  # for main() test
import qsDataframes as qsd  # for main() test
import qsSimulator as qsSim  # for main() test
import qsEvent_log as qsl

matplotlib.use('QtAgg')


class QSWindow(QMainWindow):
    """main window (GUI or view)."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("QS")
        # self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.generalLayout = QHBoxLayout()
        self.generalLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)

        fig1_cs_create(self)
        self.generalLayout.addWidget(self.ax1)

        # ax2_create(self)
        # self.generalLayout.addWidget(self.ax2)

        return


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=8, height=8, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


def fig1_cs_create(self):
    """
        agents/queue plot
    """
    self.fig1_cs = MplCanvas(self, width=8, height=8, dpi=100)
    self.fig1_cs.axes.set_ylim(0, 25)
    self.fig1_cs.axes.set_xlim(0, xmax=10)

    # trans = ax1.get_yaxis_transform()
    trans = self.fig1_cs.axes.get_yaxis_transform()
    self.fig1_cs.axes.axhline(y=s.system_max, color="red", linestyle=":")
    self.fig1_cs.axes.text(.5, s.self.system_max, 'queue full', ha='center', transform=trans)
    # self.ax1.axis("scaled")
    # self.ax1.set_autoscale_on(False)
    # -----------------


# def ax2_create(self):
#     """
#     % plot
#     """
#     self.ax2 = MplCanvas(self, width=8, height=8, dpi=100)
#     self.ax2.set_ylim(0, 1)
#     self.ax2.set_xlim(0, self.xmax, )
#     self.ax2.set_yticks(np.arange(0, 1.01, step=0.2))
#
#     # class matplotlib.ticker.PercentFormatter(xmax=100, decimals=None, symbol=’ % ’, is_latex=False)
#     # xmax:     Determines how the number is converted into a percentage.
#     # xmax is the data value that corresponds to 100%.
#     #           Percentages are computed as x / xmax * 100.
#     #           So if the data is already scaled to be percentages, xmax will be 100.
#     #           Another common situation is where xmax is 1.0.
#     # decimals: It is either an integer value or None.
#     # 			It determines the number of decimal places to place after the point.
#     # 			If None (the default), the number will be computed automatically.
#     # symbol : 	It is either a string or none that gets appended to the label.
#     # is_latex: It is a boolean value. If False, reserved LaTeX characters in symbol are eliminated.
#
#     self.ax2.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
#
#     # -----------------


# The function to be called anytime a slider's value changes
def update(val):
    # hrs_from = from_hrs_slider.val
    # hrs_window = 10 ** window_slider.val
    # hrs_to = hrs_from + hrs_window
    hrs_to = from_hrs_slider.val
    hrs_window = 10 ** window_slider.val
    hrs_from = hrs_to - hrs_window

    t0 = max(hrs_from * 3600.0 - 60.0, 0.0)
    t1 = hrs_to * 3600.0 + 60.0
    dflog2 = dflog.query('event_clock >= @t0 and event_clock <= @t1')

    ax1_plot_refresh(hrs_from, hrs_to)
    ax2_plot_refresh(hrs_from, hrs_to)

    # line.set_ydata(f(t, window_slider.val, max_slider.val))
    # fig.canvas.draw_idle()
    pass


def fig1_plot_refresh(hrs_from=0.0, hrs_to=1.0):
    self.ax1.set_xlim(hrs_from, hrs_to)

    x = dflog2['time_hrs'].to_numpy()
    y = dflog2['n_agents_talking'].to_numpy()
    y2 = (dflog2['n_queued_calls'] + dflog2['n_agents_talking']).to_numpy()
    ax1.fill_between(x, y, step="post", fc='b')
    ax1.fill_between(x, y, y2, step="post", fc='r')

    pass

    return


#
# def ax2_plot_refresh(hrs_from=0.0, hrs_to=1.0):
#     ax2.set_xlim(hrs_from, hrs_to)
#     x = dflog2['time_hrs'].to_numpy()
#
#     pimm = dflog2['pimm'].to_numpy()
#     pdly_ltt = dflog2['pdly_ltt'].to_numpy()
#     pdly_gtt = dflog2['pdly_gtt'].to_numpy()
#     pblk = dflog2['pblk'].to_numpy()
#
#     # probs=dflog2['pimm','pdly_ltt','pdly_gtt','pblk'].to_numpy()
#     ax2.stackplot(x, pimm, pdly_ltt, pdly_gtt, pblk, colors=['green', 'yellow', 'red', 'black'])
#
#     pass
#     return


def reset(event):
    from_hrs_slider.reset()
    window_slider.reset()


# ------------
def main():
    s = qsSim.QSlotSimulation()
    qsd.import_dataframes(s, debug=0)

    s.xmin = 0.0
    s.xmax = 1.0  # hrs
    s.system_max = 21  # agents+qslots
    # allowed_window_hrs= np.concatenate([np.linspace(.25, 5, 20), [6, 7, 8, 12,16,20,24,30,36,40,50,80,100]])

    now = dt.datetime.now()
    today = now.strftime("%Y%m%d")
    today = "_test"
    today_time = now.strftime("%Y-%m-%d %H:%M:%S")
    pickle_file = f'EventsLog{today}.pkl'

    # pickle_file = "D:\Dropbox\Dropbox\Documents\QSlots\EventsLog20220907.pkl"
    s.dflog = pd.read_pickle(pickle_file)
    # pd.TimedeltaIndex(unit='h',freq='5')
    s.dflog.set_index('time_hrs')

    s.dflog1_time_hrs_index = s.dflog.columns.get_loc('time_hrs')
    event_clock_limit = int(round(s.dflog.iloc[-1, s.dflog1_time_hrs_index], -1))
    window_max_hrs = event_clock_limit + 10.0  # hours

    infoboxApp = QApplication([])

    infoboxApp.setStyleSheet('.QLabel { font: bold 16pt;}')
    infoboxApp.setStyleSheet('.QButton { font: bold 16pt;}')
    infoboxWindow = QSWindow()

    infoboxWindow.show()
    infoboxWindow.move(0, 0)
    # infobox(model=evaluateExpression, view=infoboxWindow)
    sys.exit(infoboxApp.exec())

    if false:
        ax1_plot_refresh(0.0, hrs_to=xmax)

        # adjust the main plot to make room for the sliders
        plt.subplots_adjust(left=0.25, bottom=0.25)

        # Make a horizontal slider to control the frequency.
        axmax = plt.axes([0.25, 0.1, 0.65, 0.03])
        from_hrs_slider = Slider(
            ax=axmax,
            label='end time (hours)',
            valmin=1.0,
            valmax=event_clock_limit,
            valstep=1.0,
            valinit=xmax,
        )

        # Make a vertically oriented slider to control the amplitude
        axwindow = plt.axes([0.1, 0.25, 0.0225, 0.63])

        # window_slider = Slider(
        #     ax=axwindow,
        #     label="time window (hours)",
        #     valmin=0.25,
        #     valmax=window_max_hrs,
        #     valstep=allowed_window_hrs,
        #     valinit=1,
        #     orientation="vertical"
        # )

        window_slider = Slider(
            ax=axwindow,
            label="time window (hours)",
            valmin=0.0,
            valmax=2,
            # valstep=allowed_window_hrs,
            valinit=0.0,
            orientation="vertical"
        )

        # register the update function with each slider
        from_hrs_slider.on_changed(update)
        window_slider.on_changed(update)

        # Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
        resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
        button = Button(resetax, 'Reset', hovercolor='0.975')
        button.on_clicked(reset)

        plt.show(block=True)

        pass


if __name__ == '__main__':
    main()
