import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt  # for main() test

from matplotlib.transforms import Bbox
from matplotlib import patches

import qsSimulator as qsSim  # for main() test
import qsDataframes as qsd  # for main() test

from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from typing import Any
import re

import qsConstantsDfs as r
import qsConstantsDfcomb as c

import qsCalls as qsc

#  from cust import *

matplotlib.use('TkAgg')
plt.ion()


def result_box_init(s, val, cell_rc=(9, 1), cell_xy=(0, 0), w=14, h=14, fe='b', fc='', label="time", debug=0):
    """creates output box at output_xy (or output_rc)"""
    if cell_xy == (0, 0):
        cell_xy = (cell_rc[1] * 16.0 - 8.0, cell_rc[0] * 16.0 - 8.0)

    # cust.cir_xy = cir_xy
    # cust.cell_rc = cell_rc
    # cust.cir_r = cir_r
    # cust.cir_fc = cir_fc

    result_box = plt.Rectangle(xy=cell_xy, width=w, height=h, fe=fe, fc=fc, text=label)

    if debug > 0:
        s.plot.add_patch(result_box)

    return result_box


def cell_animate(cycle_time, cir, path_array):
    """animates call movement specified in pathArray"""
    if cir is not None:
        n_ticks = len(path_array)
        for iTick in range(0, n_ticks):
            (new_x, new_y) = path_array[iTick]
            # ----------------------
            cir.center = (new_x, new_y)
            # ----------------------
            plt.pause(cycle_time / 1000)

    return


def call_remove_from_q_animate(s, cycle_time=1, debug=0):
    for i_tick in range(0, 17):
        # update new_x/New_y
        s.dfcomb['new_x'] = s.dfcomb.iloc[:, c.X0 + i_tick]
        s.dfcomb['new_y'] = s.dfcomb.iloc[:, c.Y0 + i_tick]

        for i_comb in range(r.QSLOT01, r.QSLOT16 + 1):  # dfcomb has same number of rows as dfs
            cust_ = s.dfs.iat[i_comb, c.CUST]
            if cust_ is None:  # not isinstance(cust_, Cust):  # np.isnan(cust_) or (cust_ is None):
                # no more queued calls
                break
            if isinstance(cust_.cir, plt.Circle):  # cir is not None:
                new_x = s.dfcomb.iat[i_comb, c.NEW_X]
                new_y = s.dfcomb.iat[i_comb, c.NEW_Y]
                # print(i_comb,i_tick,new_x,new_y)
                pass
                cust_.cir.center = (new_x, new_y)
            else:
                break

            pass
        plt.pause(cycle_time / 1000)
    return


# --------------------------
def plot_create(self):
    """main plot creation"""
    self.fig = plt.figure()
    self.fig.set_dpi(100)
    self.fig.set_size_inches(9, 9)

    self.ax0 = self.fig.add_subplot()
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

    return self.ax0


def plot_add_frame(s, n_agents_max, n_qslots_max, debug=0):
    """adds lines to plot"""
    for row in s.dff.itertuples(index=False, name=None):
        # returns tuple (i1,j1,i2,j2)
        # display(row)
        row_type = row[4]
        row_mod = row[5]

        if (row_type == 'A') & (row_mod > n_agents_max):
            pass
        elif (row_type == 'Q') & (row_mod > n_qslots_max):
            pass
        else:
            plot_line(s.dff, row)
    return


def plot_line(s, line, lw=1, line_color='b', debug=0):
    """draws a line [(x1,x2),(y2,y2)]"""
    if debug > 0:
        print(line[1], line[3], line[0], line[2])

    plt.plot((line[1], line[3]), (line[0], line[2]), c=line_color, lw=lw)
    # plot expects (x1,x2),(y1,y2)
    # we supply coord in row,col
    # i1,j1 i2,j2
    # so (j1,j2) (i1,i2)
    #    (1,3) (0,2)
    return


def cir_init(s, cust, cell_rc=(0, 0), cir_xy=(0, 0), cir_r=8, cir_fc='y', plot_flag=0):
    """creates cir to cust at cir_xy (or cell_rc)"""
    if cir_xy == (0, 0):
        cir_xy = (cell_rc[1] * 16.0 - 8.0, cell_rc[0] * 16.0 - 8.0)

    cust.cir_xy = cir_xy
    cust.cell_rc = cell_rc
    cust.cir_r = cir_r
    cust.cir_fc = cir_fc

    cust.cir = plt.Circle(cir_xy, cir_r, fc=cir_fc)

    if plot_flag > 0:
        cir_plot(s, cust.cir)

    return cust.cir


def cir_move(cir, cir_xy):
    """moves cir to cir_xy"""
    cir.center = cir_xy
    return


def cir_plot(s, cir):
    """adds cir to plot"""
    s.plot.add_patch(cir)
    return


# def plot_active_callers(s):
#     """plots active calls specified by initial conditions"""
#     for i in range(1, s.n_agents_max + s.n_qslots_max + 1):
#         id_call = s.dfs.at[i, c.ID_CALL]
#         if id_call > 0:
#             s.cust = Cust()
#             cell = qsc.cell_rc_from_cell_index(s, i)
#
#             cir = qsp.cir_plot(s, cell)
#             s.dfs.at[i, 'cust'] = cir
#     return
#
#
# #     """
# #         from iterrows() in manual
# #         --------------------------
# #         You should **never modify** something you are iterating over.
# #             This is not guaranteed to work in all cases.
# #             Depending on the data types,
# #                 the iterator returns a copy and not a view,
# #                 and writing to it will have no effect.
# #         -----------------------------
# #         seems to be ok but I moved to using indexs to be safe
# #         """
# # pass

def call_move_a_to_b(cells, debug=0):
    """moves call based on list of cells = tuples (row,col)"""
    """ general routine to move a call from cell A to cell B"""
    """
    cells expect list of tuples (row,col)
    it returns an numpy array of (center_,center_y) with 8 steps per cell traversed
    """
    """    
    cells
    ((2, 4), (3, 4), (3, 9))       
    """
    a = np.asarray(cells)
    n_cells_input = len(a)
    delta_array = np.zeros((n_cells_input, 2))
    """
    a
    array([[2, 4],
       [3, 4],
       [1, 9]])

    delta_array
    array([[0, 0],
        [0, 0],
        [0, 0]])    
    """
    # compute number of cells and populat dx and dy

    n_cells_moved = 0
    for k in range(0, n_cells_input - 1):  # count one less than total length
        a_diff = a[k + 1] - a[k]
        delta_array[k] = a_diff[1] * 2, a_diff[0] * 2
        n_diff = np.sum(a_diff)

        n_cells_moved += np.abs(n_diff)
        if debug > 0:
            print(k, a_diff, n_diff, n_cells_moved)

    # build path_array

    path_array = np.zeros((n_cells_input * 8, 2))
    row0, col0 = a[0]
    x = 16 * col0 - 8
    y = 16 * row0 - 8

    j = 0
    for k in range(0, n_cells_input):
        dx, dy = delta_array[k]
        for i in range(0, 8):
            path_array[j] = (x, y)
            if debug > 0:
                print(k, x, y)

            x += dx
            y += dy
            j += 1
            pass
    pass
    return path_array


"""
0 [-1  0] -1 1
1 [0 5] 5 6

0 56 24
0 56.0 22.0
0 56.0 20.0
0 56.0 18.0
0 56.0 16.0
0 56.0 14.0
0 56.0 12.0
0 56.0 10.0

1 56.0 8.0
1 66.0 8.0
1 76.0 8.0
1 86.0 8.0
1 96.0 8.0
1 106.0 8.0
1 116.0 8.0
1 126.0 8.0

2 136.0 8.0
2 136.0 8.0
2 136.0 8.0
2 136.0 8.0
2 136.0 8.0
2 136.0 8.0
2 136.0 8.0
2 136.0 8.0

"""


# pathArray=call_move_a_to_b([(2,4),(1,4),(1,9)])
# display(pathArray)


def call_move_to_next_av_agent(s, cust, from_rc, to_rc, cycle_time=1):
    """moves call from cells[-1] to Next available Agent
    @type from_rc: object
    """
    cells = []
    cells.append(from_rc)
    # cells: list[tuple[Any, Any] | tuple[int, int]] = from_rc

    cell0 = cells[-1]
    cell1 = qsc.cell_next(cell0, 'D', steps=1)
    cells.append(cell1)

    to_row, to_col = to_rc
    if to_col > 1:
        # move right next_free_agent
        cell0 = cells[-1]
        cell1 = qsc.cell_next(cell0, 'R', to_col - 1)
        cells.append(cell1)


    cells.append(to_rc)
    path_array = call_move_a_to_b(cells)
    cell_animate(cycle_time, cust.cir, path_array)

    return


def main():
    s = qsSim.QSlotSimulation()

    qsd.import_dataframes(s, debug=0)

    plot = plot_create(s)
    plot_add_frame(s, n_agents_max=5, n_qslots_max=16, debug=1)

    secs = 5000
    etime = dt.timedelta(seconds=secs)

    time_str=f'{etime}'
    #
    cell_rc = (9, 1)
    w = 16
    h = 14
    x = cell_rc[1] * 16.0 - 8 - w / 2
    y = cell_rc[0] * 16.0 - 8 - h / 2

    # plt.rcParams["figure.figsize"] = [7.00, 3.50]
    # plt.rcParams["figure.autolayout"] = True
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    ax = plt.gca()

    rect = plt.Rectangle((x, y), w, h, edgecolor='k',
                         facecolor="grey", linewidth=1, alpha=0.2)

    ax.add_patch(rect)

    #  An Artist instance. The xy value (or xytext) is interpreted as a fractional coordinate of the bbox
    #  (return value of get_window_extent) of the artist:

    # an1 = ax.annotate("Test 1", xy=(0.5, 0.5), xycoords="data",
    #                   va="center", ha="center",
    #                   bbox=dict(boxstyle="round", fc="w"))

    # an2 = ax.annotate("Test 2", xy=(1, 0.5), xycoords=rect,  # (1, 0.5) of the an1's bbox
    #                   xytext=(30, 0), textcoords="offset points",
    #                   va="center", ha="left",
    #                   bbox=dict(boxstyle="round", fc="w"),
    #                   arrowprops=dict(arrowstyle="->"))

    ax.annotate("Test 2", xy=(0.5, 0.9), xycoords=rect,
                xytext=(0, 0), textcoords="offset points",
                va="top", ha="center",
                color='black', weight='bold', fontsize=10)

    ax.annotate(time_str, xy=(0.5, 0.5), xycoords=rect,
                xytext=(0, 0), textcoords="offset points",
                va="top", ha="center",
                color='black', weight='bold', fontsize=12)


    pass

    """  
    rx, ry = rect.get_xy()
    cx = rx + rect.get_width() / 2.0
    cy = ry + rect.get_height() / 2.0
    ax.annotate("Rectangle", (cx, cy), color='black', weight='bold', fontsize=10, ha='center', va='center')
    """

    # my_blit_box = Bbox.from_bounds(x, y, w, h)
    # str_ = f'Time\n{etime}'
    # cell=plt.text(x, y, str_,bbox={'facecolor': 'red', 'alpha': 0.2, 'pad': 0})

    # result_time = qsp.result_box_init(s, s.event_clock, cell_rc=(9, 1), cell_xy=(0, 0), w=14, h=14, fe='b', fc='',
    #                                   label="time", debug=s.plot_flag)

    return


if __name__ == "__main__":
    main()

pass
