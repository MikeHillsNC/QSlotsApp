import sys
from functools import partial

import PyQt6

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

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

import pandas as pd
import numpy as np
import datetime as dt  # for main() test

from dataclasses import dataclass
from typing import Any

import qsPlot_PyQt as qsp  # for main() test
import qsDataframes as qsd  # for main() test
import qsSimulator as qsSim  # for main() test
import qsEvent_log as qsl

ERROR_MSG = "ERROR"
WINDOW_HEIGHT = 900
WINDOW_WIDTH = 900
DISPLAY_HEIGHT = 35
BUTTON_SIZE = 40

QSHCELLS = 8
QSVCELLS = 8
CELLSIZE = 16

format_strings = {
    'INT': '{:>8,.0f}',
    'PER1': '{:.1%}',
    'PER2': '{:.2%}',
    'HOURS': "{:.2f} hours",
    'SECS': "{:.0f} secs",
    'STR': "{}"
}


class QSWindow(QMainWindow):
    """main window."""

    def __init__(self):
        super().__init__()

        self.s = qsSim.QSlotSimulation()
        qsd.import_dataframes(self.s, debug=0)

        self.setWindowTitle("Queueing simulator")

        self.generalLayout = QVBoxLayout()
        self.generalLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)

        self._createInfobox()
        self.generalLayout.addLayout(self.infobox)

        self.qsplot_canvas = QSPlotCanvas(self)

        self.generalLayout.addWidget(self.qsplot_canvas)

        self.buttons = self._createButtons(self.qsplot_canvas)
        self.generalLayout.addLayout(self.buttons)
        return

    def _createInfobox(self):
        self.infobox = QHBoxLayout()
        self.infobox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.infobox.setSpacing(0)

        # label1 = InfoLabel(self, '00:00', '')
        label1 = QLabel('00:00')
        label1.setWordWrap(True)
        label1.setFixedWidth(100)
        label1.setFrameShape(QFrame.Shape.Box)
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infobox.addWidget(label1)

        text1 = 'New call'
        text2 = 'Ans imm by agent 1'
        newline = '\n'
        if len(text2) > 0:
            text = f"{text1}{newline}{text2}"
        else:
            text = text1
        label2 = QLabel(text)
        label2.setWordWrap(True)
        label2.setFixedWidth(300)
        label2.setFrameShape(QFrame.Shape.Box)
        label2.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.infobox.addWidget(label2)

        text1 = 'Talk time'
        text2 = '120 secs'
        newline = '\n'  # char(10)
        if len(text2) > 0:
            text = f"{text1}{newline}{text2}"
        else:
            text = text1
        label3 = QLabel(text)
        label3.setWordWrap(True)
        label3.setFixedWidth(120)
        label3.setFrameShape(QFrame.Shape.Box)
        label3.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.infobox.addWidget(label3)

        text1 = 'Wait time'
        text2 = '120 secs'
        newline = '\n'
        if len(text2) > 0:
            text = f"{text1}{newline}{text2}"
        else:
            text = text1
        label4 = QLabel(text)
        label4.setWordWrap(True)
        label4.setFixedWidth(120)
        label4.setFrameShape(QFrame.Shape.Box)
        label4.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.infobox.addWidget(label4)

        return

    def _createButtons(self, canvas):
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)

        reset = QPushButton("reset")

        reset.clicked.connect(self.qsplot_canvas.reset_btn)

        # reset.clicked.connect(self.reset_btn(canvas))
        hbox.addWidget(reset)

        step = QPushButton("step")
        step.clicked.connect(self.qsplot_canvas.step_btn)
        hbox.addWidget(step)

        return hbox


class QSPlotCanvas(FigureCanvasQTAgg):
    """canvas is a widget"""

    def __init__(self, parent=None, width=8, height=8, dpi=100, debug=0):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax0 = fig.add_subplot(111)

        self.ax0.set_xlim(0, 128)
        self.ax0.set_ylim(0, 128)
        self.ax0.axis("scaled")
        # self.ax0.set_autoscale_on(False)

        if debug > 0:
            self.ax0.xaxis.set_major_locator(MultipleLocator(16))
            self.ax0.xaxis.set_major_formatter('{x:.0f}')
            self.ax0.xaxis.set_minor_locator(MultipleLocator(8))

            self.ax0.yaxis.set_major_locator(MultipleLocator(16))
            self.ax0.yaxis.set_major_formatter('{x:.0f}')
            self.ax0.yaxis.set_minor_locator(MultipleLocator(8))

        super().__init__(fig)

        xdata = [16, 112, 112]
        ydata = [112, 112, 48]
        self.ax0.plot(xdata, ydata, 'r')
        # self.show()

        pass

    def reset_btn(self):
        """creates cir to cust at cir_xy (or cell_rc)"""
        cir = cir_init(self, cell_rc=(8, 1), plot_flag=1)
        return

    def step_btn(self):
        xdata = [16, 16]
        ydata = [48, 96]
        self.ax0.plot(xdata, ydata, 'b')
        self.draw()
        pass

    def circle_btn(self, xdata=[16, 16], ydata=[48, 96]):
        self.ax0.plot(xdata, ydata, 'r')
        self.draw()
        pass


def cir_init(canvas, cell_rc=(0, 0), cir_xy=(0, 0), cir_r=8, cir_fc='y', plot_flag=0):
    """creates cir to cust at cir_xy (or cell_rc)"""
    if cir_xy == (0, 0):
        cir_xy = (cell_rc[1] * 16.0 - 8.0, cell_rc[0] * 16.0 - 8.0)

    # cust.cir_xy = cir_xy
    # cust.cell_rc = cell_rc
    # cust.cir_r = cir_r
    # cust.cir_fc = cir_fc

    cir = plt.Circle(cir_xy, cir_r, fc=cir_fc)

    if plot_flag > 0:
        canvas.ax0.add_patch(cir)
        canvas.draw()

    return cir


#
# def cir_move(cir, cir_xy):
#     """moves cir to cir_xy"""
#     cir.center = cir_xy
#     return


def cir_plot(canvas, cir):
    """adds cir to plot"""
    canvas.ax0.plot.add_patch(cir)
    return


def plot_add_frame(self, n_agents_max, n_qslots_max, debug=0):
    """adds lines to plot"""
    for row in self.s.dff.itertuples(index=False, name=None):
        # returns tuple (i1,j1,i2,j2)
        # display(row)
        row_type = row[4]
        row_mod = row[5]

        if (row_type == 'A') & (row_mod > n_agents_max):
            pass
        elif (row_type == 'Q') & (row_mod > n_qslots_max):
            pass
        else:
            plot_line(self.canvas, row)

    return


def plot_line(canvas, row):
    """draws a line .QGraphicsScene.addLine(x1, y1, x2, y2[, pen=QPen()])"""
    # we supply coord in row,col
    # i1,j1 i2,j2
    # y1,x1,y2,x2
    # so (j1,j2) (i1,i2)
    #    (1,3) (0,2)

    # scene.addLine(112, 16, 112, 112)

    # print(row[1], row[3], row[0], row[2])
    # self.canvas.ax0.plot(self.xdata, self.ydata, 'r')

    # canvas.ax0.plot(self.xdata, self.ydata, 'r')
    canvas.ax0.plot([row[1], row[3]], [row[0], row[2]], 'r')
    canvas.draw()
    return


class ax1_Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=8, height=8, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = fig.add_subplot(111)

        self.ax0.set_xlim(0, 128)
        self.ax0.set_ylim(0, 128)
        self.ax0.axis("scaled")
        self.ax0.set_autoscale_on(False)

        self.ax0.xaxis.set_major_locator(MultipleLocator(16))
        self.ax0.xaxis.set_major_formatter('{x:.0f}')
        self.ax0.xaxis.set_minor_locator(MultipleLocator(8))

        self.ax0.yaxis.set_major_locator(MultipleLocator(16))
        self.ax0.yaxis.set_major_formatter('{x:.0f}')
        self.ax0.yaxis.set_minor_locator(MultipleLocator(8))

        super().__init__(fig)


# ________________________
refresh_cols = []
refresh_format_strings = []
refresh_tas = []

ann_id = 0  # module global


@dataclass
class InfoBox:
    sim_subplot: Any
    cell_rc: tuple[Any, Any]

    label: str = 'label'

    val1: float = 0.0
    val1f: Any = 'PER1'
    val1fs: Any = None
    val1str: Any = None
    val1ann: Any = None

    val2: Any = None
    val2f: Any = None
    val2fs: Any = None
    val2str: Any = None
    val2ann: Any = None

    width: float = 16.0
    height: float = 14.0

    x: float = 0.0
    y: float = 0.0

    ib_patch: Any = None

    texts: tuple = (None, None, None)

    #  rect: plt.Rectangle = None

    id: int = 0

    def __post_init__(self):
        global infobox_id
        infobox_id += 1
        self.id = infobox_id

        self.x = self.cell_rc[1] * 16.0 - 8 - self.width / 2
        self.y = self.cell_rc[0] * 16.0 - 8 - self.height / 2
        self.rect = plt.Rectangle((self.x, self.y), self.width, self.height, edgecolor='k',
                                  facecolor="grey", linewidth=1, alpha=0.2)

        self.ib_patch = self.sim_subplot.add_patch(self.rect)

        self.val1fs = format_strings.get(self.val1f, None)
        if self.val1fs is None:
            self.val1fs = self.val1f

        if self.val2 is not None:
            self.val2fs = format_strings.get(self.val2f, None)
            if self.val2fs is None:
                self.val2fs = self.val2f

        pass

        self.val1ann = self.sim_subplot.annotate(
            self.label, xy=(0.5, 0.89), xycoords=self.ib_patch,
            xytext=(0, 0), textcoords="offset points",
            va="top", ha="center",
            color='black', weight='bold', fontsize=10)
        #
        # #  ann = plt.annotate("{:.2f}".format(n[j]), xy=(n[j], f(n[j])), color="purple", fontsize=12
        # #  ann.remove()
        #
        val1str = self.val1fs.format(self.val1)
        self.val1ann = plt.annotate(
            val1str, xy=(0.5, 0.55), xycoords=self.ib_patch,
            xytext=(0, 0), textcoords="offset points",
            va="top", ha="center",
            color='black', weight='bold', fontsize=10)

        if self.val2 is not None:
            val2str = self.val2fs.format(self.val2)
            self.val2ann = plt.annotate(
                val2str, xy=(0.5, 0.22), xycoords=self.ib_patch,
                xytext=(0, 0), textcoords="offset points",
                va="top", ha="center",
                color='black', weight='bold', fontsize=10)

        return self.ib_patch

    def __repr__(self):
        # "{l}={v:.1%}".format(l=self.label, v=self.val1)
        val1str = self.val1fs.format(self.val1)
        if self.val2 is None:
            val2str = ""
        else:
            val2str = f",{self.val2fs.format(self.val2)}"
        return f"cell_rc {str(self.cell_rc)} {self.label}={val1str}{val2str}"


def set_val1(self, val1):
    ann1 = self.ib[0].val1ann
    val1str = self.ib[0].val1fs.format(val1)
    ann1.set_text(val1str)


def set_val2(self, val2):
    val2str = self.ib[1].val1fs.format(val2)
    self.ib[1].val1ann.set_text(val2str)


def infobox_init(s, event_log_row0, ax):
    df = pd.DataFrame([event_log_row0])
    s.textprops = dict(color='k', fontsize=16, fontweight='bold')
    vals0 = []
    # 0
    vals_load(s, vals0, 'Event', 'STR', df)
    vals_load(s, vals0, 'index', 'INT', df, refresh=True, val_default=100000)

    # 2
    vals_load(s, vals0, 'Clock', 'STR', df)
    vals_load(s, vals0, 'event_clock_td_str', 'STR', df, refresh=True, val_default='100:10:10')

    # 4
    vals_load(s, vals0, 'ev_type', 'STR', df, refresh=True, val_default='arr')
    vals_load(s, vals0, '', 'STR', df)

    # 6
    vals_load(s, vals0, 'event', 'STR', df, refresh=True, val_default='Departed')
    vals_load(s, vals0, 'event_mod', 'STR', df, refresh=True, val_default='after imm answer')

    # 8
    vals_load(s, vals0, 'talk', 'STR', df)
    vals_load(s, vals0, 'talk_time', 'SECS', df, refresh=True, val_default=150)

    # 10
    vals_load(s, vals0, 'wait', 'STR', df)
    vals_load(s, vals0, 'wait_time', 'SECS', df, refresh=True, val_default=1000)

    pass

    # refresh_cols = []
    # refresh_format_strings = []
    # refresh_tas = []
    # [0=name, 1=colindex, 2=format_code, 3=format_string, 4=refresh, 5=ta, 6=default]
    for row in vals0:
        if row[4]:
            refresh_cols.append(row[1])
            refresh_format_strings.append(row[3])
            refresh_tas.append(row[5])

    # print(refresh_cols)

    pass
    return


def infobox_update(df, clear=False):
    logrow = df.iloc[0, refresh_cols]
    for icol in range(len(refresh_cols)):
        val = logrow[icol]
        valfs = refresh_format_strings[icol]
        valta = refresh_tas[icol]
        # x = "nice" if is_nice else "not nice"
        valstr = '    ' * 4 if clear else valfs.format(val)
        valta.set_text(valstr)
        plt.pause(.1 / 1000)
    return


def vals_load(s, vals, name, format_code, df, val_default=None, refresh=False):
    colname = name

    if refresh:
        colindex = df.columns.get_loc(name)
    else:
        colindex = 0

    format_code = format_code
    format_string = format_strings.get(format_code, None)
    # set default
    if val_default is None:
        valstr = name
    else:
        valstr = format_string.format(val_default)
    # row[5].set_text(valstr)
    ta = TextArea(valstr, textprops=s.textprops)

    vals.append([name, colindex, format_code, format_string, refresh, ta])
    return


def main():
    """main function."""

    infoboxApp = QApplication([])

    infoboxApp.setStyleSheet('.QLabel { font: bold 16pt;}')
    infoboxApp.setStyleSheet('.QButton { font: bold 16pt;}')
    infoboxWindow = QSWindow()

    infoboxWindow.show()
    infoboxWindow.move(0, 0)
    # infobox(model=evaluateExpression, view=infoboxWindow)
    sys.exit(infoboxApp.exec())


if __name__ == "__main__":
    main()
    # demo()
pass
