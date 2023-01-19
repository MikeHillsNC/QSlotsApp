import pandas as pd
import datetime as dt
import numpy as np
# import matplotlib.pyplot as plt

import os

# from traitlets import Int

import qsConstantsDfs as r
import qsConstantsDfcomb as c

import qsEvent_log as qsl
from cust import *

# from config import events_df
events = []  # empty list
events_all = []  # all events
events_df = pd.DataFrame(columns=['ev_clock', 'ev_ia_clock', 'ev_type', 'agent', 'talk_time', 'abn_Time'])
events_all_df = pd.DataFrame(columns=['ev_clock', 'ev_ia_clock', 'ev_type', 'agent', 'talk_time', 'abn_Time'])


def secs_to_timedelta(x):
    t0 = round(x * 1000, 1)
    t1 = dt.timedelta(milliseconds=t0)
    return t1


# random numbers use low=0.17 to ensure nothing less than a second is generated

def ia_time_rand(s):
    ia = np.round((-np.log(1 - (np.random.uniform(low=0.017, high=1.0))) * s.inter_arrival_time_av / s.arrival_boost),
                  s.event_precision)
    return ia


def talk_time_rand(s):
    x = np.round((-np.log(1 - (np.random.uniform(low=0.017, high=1.0))) * s.talk_time_av * s.arrival_boost),
                 s.event_precision)
    return x


def abn_time_rand(s):
    if s.abn_time > 0:
        abn = round((-np.log(1 - (np.random.uniform(low=0.017, high=1.0))) * s.abn_time_av), s.event_precision)
    else:
        abn = 0.0
    return abn


def next_free_agent(s):
    """updates next_free_agent"""
    # TODO write code to compute ev_agent who has ben free longest if multiple agents are free
    # TODO until then we choose first available
    next_free_agent_ = 0
    if s.n_agents_talking < s.n_agents_sim:
        for i in range(1, s.n_agents_sim + 1):
            if cell_agent_status(s, i) == r.CELL_IDLE:
                next_free_agent_ = i
                break

    pass
    return next_free_agent_


def call_new(s, cust, cycle_time=1, debug=0):
    """main New call routine"""
    # create new cust
    cell_rc_initial = cell_rc_from_cell_index(s, r.NEWCALL0)

    # --------------
    cust.cir = qsp.cir_init(s, cust, cell_rc_initial, plot_flag=s.plot_flag)
    # this command also populates cell NEWCALL0 with patch as new call ready for moving to destination
    # --------------

    # what is current state of system
    n_queued_calls_, s.next_free_qslot = calls_in_q(s)
    s.n_agents_talking = calls_in_agents(s)

    # cust.id_call = s.id_call
    cust.ev_clock = s.ev_clock
    cust.ev_ia_time = s.ev_ia_time
    cust.ev_type = s.ev_type
    cust.ev_agent = s.ev_agent
    cust.ev_talk_time_proj = s.ev_talk_time_proj
    cust.ev_abn_time_proj = s.ev_abn_time_proj

    cust.t_arr = s.ev_clock

    # ----------------------
    qsl.event_new_log_row(s, cust, debug=s.debug_test)
    # ----------------------

    cells = []
    if s.plot_flag > 0:
        # a new call is loaded into cell NEWCALL0
        # from there it will moved to an agent/the q/blocked imm
        # see qslots.xlsx for diagram of cells
        # start list of r,c tuples describing path call will take
        cells.append(cell_rc_from_cell_index(s, r.NEWCALL0))

    if s.n_queued_calls == s.n_qslots_sim:
        # ----------
        # imm blocked
        # ----------
        cust.t_arr = s.ev_clock
        cust.t_ser = 0.0
        cust.t_dep = cust.t_arr
        cust.state = CS.COMPLETED_ABN

        s.n_arr += 1  # num of calls arrived
        s.n_blk_imm += 1  # num of calls blocked (Q full)
        s.n_dep += 1  # num of calls leaving (all reasons)
        s.n_dep_imm += 1  # num of calls leaving agent having been imm answered

        # ----------------------
        qsl.event_new_log_row(s, cust, debug=s.debug_test)
        # ----------------------

        if s.plot_flag > 0:
            cells.append((8, 8))     # trmp fixuintil we add r.DEPCALL0
            cells.append(cell_rc_from_cell_index(s, r.BLOCKED))
            path_array = qsp.call_move_a_to_b(cells)
            qsp.cell_animate(cycle_time, cust.cir, path_array)

    else:
        # ----------
        # call enters system
        # ----------
        if s.n_agents_talking < s.n_agents_sim:
            # ----------
            # imm answer
            # ----------
            cust.state = CS.ANS_IMM
            cust.t_arr = s.ev_clock
            cust.t_ser = cust.t_arr
            cust.t_dep = round(cust.t_arr + cust.ev_talk_time_proj, s.event_precision)
            agent_index = next_free_agent(s)
            cust.agent = agent_index
            cust.qslot = 0

            s.n_agents_talking += 1
            s.n_ans_imm += 1
            s.n_arr += 1  # num of calls arrived

            # create departure event
            dep_event_ = [cust.t_dep, cust.ev_ia_time, EV.DEP, cust.agent,
                          s.ev_talk_time_proj, s.ev_abn_time_proj]
            events.append(dep_event_)
            events_all.append(dep_event_)
            events_display(s, debug=s.debug_test)

            # ----------
            # update dfs imm served call
            call_data_update(s, r.AGENTS[agent_index], cust)
            # ----------

            # ----------------------
            qsl.event_new_log_row(s, cust, debug=s.debug_test)
            # ----------------------

            if s.plot_flag > 0:
                # move cust from cells[-1] to Next available Agent
                cells.append(cell_rc_from_cell_index(s, r.NEXTAGENT1))
                l_next_free_agent = cust.agent
                if l_next_free_agent > 1:
                    # move right next_free_agent
                    cell0 = cells[-1]
                    cell1 = cell_next(cell0, 'R', l_next_free_agent - 1)
                    cells.append(cell1)

                cell_destination_index = r.AGENTS[l_next_free_agent]
                cells.append(cell_rc_from_cell_index(s, cell_destination_index))
                path_array = qsp.call_move_a_to_b(cells)
                qsp.cell_animate(cycle_time, cust.cir, path_array)

        else:
            # ----------
            # enter Q
            # ----------
            cust.state = CS.IN_Q
            cust.t_arr = s.ev_clock
            cust.t_ser = 0.0
            cust.t_dep = 0.0
            cust.agent = 0
            cust.qslot = s.next_free_qslot

            # TODO create potential abandonment event

            # --------------------
            s.n_arr += 1  # num of calls arrived
            # s.n_blk_imm +=1     # num of calls blocked (Q full)
            # s.n_abn_imm +=1     # num of calls abandoning if no ev_agent immediately available
            # s.n_abn_dly +=1     # num of calls abandoning after spending some time in Q
            s.n_dly += 1  # num of calls entering Q (total)
            # s.n_dly_t +=1       # num of calls entering Q whose delay before answer exceeds T seconds
            # s.n_ans_imm +=1     # num of calls answered immediately
            # s.n_ans_dly +=1     # num of calls answered who had been delayed
            # s.n_dep +=1         # num of calls leaving (all reasons)
            # s.n_dep_imm +=1     # num of calls leaving agent having been imm answered
            # s.n_dep_dly +=1     # num of calls leaving agent having been delayed

            # s.n_agents_talking +=1  # current number of Agents talking
            # s.n_agents_talking -=1  # current number of Agents talking
            s.n_queued_calls += 1  # current number of calls in Q
            # s.n_queued_calls -=1  # current number of calls in Q
            # -----------------------------

            # ----------
            # update dfs queued call
            cell_destination_index = r.QSLOTS[s.next_free_qslot]
            call_data_update(s, cell_destination_index, cust)
            # ----------

            # ----------------------
            qsl.event_new_log_row(s, cust, debug=s.debug_test)
            # ----------------------

            if s.plot_flag > 0:  # ==-1:
                cells = [cell_rc_from_cell_index(s, r.NEWCALL0)]
                # cell_destination_index = r.QSLOTS[s.next_free_qslot]
                # call_data_update(s, cell_destination_index, cust)
                path_array = call_path_into_q(s, cells, debug=0)
                cycle_time = .2
                qsp.cell_animate(cycle_time, cust.cir, path_array)
                pass

    # # ----------------------
    # qsl.event_new_log_row(s, cust, debug=s.debug_test)
    # # ----------------------

    return


def call_q_to_a(s, cust, agent_index):
    """moves call from head of Q to QSLOT00 - shifts remains queued calls returns cust"""

    # call_remove_from_q(s, cycle_time=s.cycle_time, debug=0)
    #
    # cust.state = CS.ANS_DELAY
    # # ----------------------
    # qsl.event_new_log_row(s, cust, debug=s.debug_test)
    # # ----------------------

    if s.plot_flag > 0:
        from_rc = cell_rc_from_cell_index(s, r.QSLOT00)
        to_rc = cell_rc_from_cell_index(s, r.AGENTS[agent_index])
        qsp.call_move_to_next_av_agent(s, cust, from_rc, to_rc, cycle_time=s.cycle_time)

    return


def events_display(s, debug=0):
    global events_df, events, events_all_df, events_all
    if debug > 0:
        events_df = pd.DataFrame(data=events)
        events_all_df = pd.DataFrame(data=events_all)

    return


def events_sort(s):
    events.sort(key=lambda x: x[0])  # sort by ev_clock
    return


def events_add_arr(s, debug=0, reset=0):
    if reset == 1:
        ll = [0.0, 0.0, EV.SKIP, 0, 0.0, 0.0]
        events.append(ll)
    else:
        s.ev_ia_time = ia_time_rand(s)
        s.t_highest_arr_time_in_events = s.t_highest_arr_time_in_events + s.ev_ia_time
        talk_time_proj = talk_time_rand(s)
        abn_time_proj = abn_time_rand(s)

        event_ = [s.t_highest_arr_time_in_events, s.ev_ia_time, EV.ARR, 0, talk_time_proj, abn_time_proj]
        events.append(event_)
        #  if s.debug_test > 0:
        events_all.append(event_)
        pass
    return


def call_next_event(s, debug=0):
    # global events_df
    events_len = len(events)
    if events_len > 0:
        events_sort(s)
    # --------------------------
    # do we need more arrivals?
    # --------------------------
    n_arr_events = 0
    # max_arr_time = 0.0
    for i in range(events_len):
        ev_clock_, _, ev_type_, _, _, _ = events[i]
        if ev_type_ == EV.ARR:
            n_arr_events += 1
            s.t_highest_arr_time_in_events = max(s.t_highest_arr_time_in_events, ev_clock_)

    if n_arr_events < 10:
        for i in range(10):
            events_add_arr(s)
        events_sort(s)

    # # events_display(s, debug=s.debug_test)
    # if s.debug_test > 0:
    #     events_df = pd.DataFrame(
    #         columns=['ev_clock', 'ev_ia_time', 'ev_type', 'ev_agent', 'ev_talk_time_proj', 'ev_abn_time_proj'],
    #         data=events)
    #     events_all_df = pd.DataFrame(
    #         columns=['ev_clock', 'ev_ia_time', 'ev_type', 'ev_agent', 'ev_talk_time_proj', 'ev_abn_time_proj'],
    #         data=events_all)

    new_event = events.pop(0)  # pop als remove row
    pass
    return new_event


def call_dep(s, cust_departing, agent_index, cycle_time=1):
    """ removes call from ev_agent - replaces with call from Q"""
    if s.plot_flag > 0:
        cells = []
        cell0 = cell_rc_from_cell_index(s, r.AGENTS[agent_index])
        cells.append(cell0)
        cell1 = cell_next(cell0, 'D')
        cells.append(cell1)
        cells.append((1, 9))

        path_array = qsp.call_move_a_to_b(cells)
        qsp.cell_animate(cycle_time, cust_departing.cir, path_array)

        pass

    return


def call_path_into_q(s, cells, debug=0):
    """creates path_array for new call into next available QSlot"""
    # indexOfNextAvailableQSlot will be between 1 (Q currently empty)
    # and s.n_qslots_sim (Q has one remaining slot)
    # dfq has 96 rows from  NEWCALL0->QSLOTS[1]->QSLOTS[16]  cell 41->43->73
    # with 3 steps between centers
    # check out QSlots.xlsx

    """ 
                cell_mod  row  col    x    y
    iD_path 
    # cells 71-72 are blank cells (cell_mod=0)                             
        0               0    7    1    8  104
        1               0    7    1   12  104
        2               0    7    1   16  104
        3               0    7    1   20  104

        4               0    7    2   24  104
        5               0    7    2   28  104
        6               0    7    2   32  104
        7               0    7    2   36  104
    # cell 73 is QSLOTS[16]
        8              16    7    3   40  104
        9              16    7    3   44  104
        10             16    7    3   48  104
        11             16    7    3   52  104

        12             15    7    4   56  104
        13             15    7    4   60  104
        14             15    7    4   64  104
        15             15    7    4   68  104
        ....
        16             14    7    5   72  104
        17             14    7    5   76  104
        18             14    7    5   80  104
        19             14    7    5   84  104

        20             13    7    6   88  104
        21             13    7    6   92  104
        22             13    7    6   96  104
        23             13    7    6  100  104

        24              0    7    7  104  104
        25              0    7    7  104  100
        26              0    7    7  104   96
        27              0    7    7  104   92
    #cell 77 and 67 are turning space - blank cells (cell_mod=0) 
        28              0    6    7  104   88
        29              0    6    7  100   88
        30              0    6    7   96   88
        31              0    6    7   92   88

        32             12    6    6   88   88
        33             12    6    6   84   88
        34             12    6    6   80   88
        35             12    6    6   76   88
        ...
    cell 43 is SLOTS[1]
        92              1    4    3   40   56
        93              1    4    3   36   56
        94              1    4    3   32   56
        95              1    4    3   28   56
  
    so if the next avaiable QSLOT is the ith we need rows 0 through 
  
    """
    # compute the last row index for the ith QSLOT
    # Int64Index: 96 entries, 0 to 95
    # Data columns (total 5 columns):
    # #   Column    Non-Null Count  Dtype
    # ---  ------    --------------  -----
    # 0   cell_mod  96 non-null     int64
    # 1   row       95 non-null     int64
    # 2   col       96 non-null     int64
    # 3   x         96 non-null     int64
    # 4   y         96 non-null     int64
    # dtypes: int64(5)
    #

    # dfq = s.dfp  # s.dfQS_pathsQ
    dfq_len = len(s.dfq)
    dfq_index = 0
    for i in range(0, dfq_len):
        if s.dfq.iat[i, 0] == s.next_free_qslot:
            dfq_index = i
            break

    df = s.dfq.iloc[0:dfq_index + 1, [3, 4]]
    """
            x    y
    iD_path        
    
    4         24  104
    6         32  104
    8         40  104
    10        48  104
    12        56  104
    14        64  104
    16        72  104
    18        80  104
    20        88  104
    22        96  104
    24       104  104
    26       104   96
    28       104   88
    30        96   88
    32        88   88
    34        80   88
    36        72   88
    38        64   88
    40        56   88
    42        48   88
    44        40   88
    46        32   88
    48        24   88
    50        24   80
    52        24   72
    54        32   72
    56        40   72
    58        48   72
    60        56   72
    62        64   72
    64        72   72
    66        80   72
    68        88   72
    70        96   72
    72       104   72
    74       104   64
    76       104   56
    78        96   56
    80        88   56
    82        80   56
    84        72   56
    86        64   56
    88        56   56
    90        48   56
    92        40   56
    94        32   56

    """

    path_array = df.to_numpy()

    if debug > 0:
        display(path_array)

    return path_array


def cell_next(cell, direction, steps=1):
    """utility to specify next cell U D L R """
    row = cell[0]
    col = cell[1]
    if direction == 'D':
        row -= steps
    elif direction == 'U':
        row += steps
    elif direction == 'L':
        col -= steps
    else:
        col += steps

    return row, col


def cell_rc_from_cell_index(s, cell_index):
    """utilty to provide col,row from iSystem"""
    col = s.dfs.iat[cell_index, c.CURRENT_CL]
    row = s.dfs.iat[cell_index, c.CURRENT_RW]
    return row, col


def cell_q_status(s, i):
    """status of ith QSlot"""
    status = s.dfs.iat[r.QSLOTS[i], c.STATUS]
    return status


def cell_agent_status(s, i):
    """status of ith Agent"""
    status = s.dfs.iat[r.AGENTS[i], c.STATUS]
    return status


def calls_in_q(s):
    """updates n_queued_calls/next_free_qslot"""
    n_q_calls = 0
    for i in range(1, s.n_qslots_sim + 1):
        if cell_q_status(s, i) != r.CELL_IDLE:
            n_q_calls += 1


    next_free_qslot_ = 0
    if n_q_calls < s.n_qslots_sim:
        next_free_qslot_ = n_q_calls + 1
    else:
        next_free_qslot_ = 0

    return n_q_calls, next_free_qslot_


def calls_in_agents(s):
    """updates n_agents_talking"""
    n_a_calls = 0
    for i in range(1, s.n_agents_sim + 1):
        if s.dfs.iat[r.AGENTS[i], c.STATUS] != r.CELL_IDLE:
            n_a_calls += 1
    return n_a_calls


# IMMBLOCK='Blocked'
# INQ='In queue'
# ANSIMM='Answered immediately'
# ANSDELAY='Answered after queuing'
# COMP='Completed'

def calls_init_load(s, n_calls_a=5, n_calls_q=16, debug=0):
    """  sets initial conditions in dfs """

    s.id_call = 0
    n_calls = 0

    s.clock = 0.0
    s.ev_clock = 0.0
    s.ev_ia_time = 0.0
    for cell_index in range(r.AGENT1, r.AGENT8 + 1):

        agent_index = s.dfs.iat[cell_index, c.CELL_MOD]
        if agent_index <= n_calls_a:
            s.n_arr += 1  # num of calls arrived
            s.n_ans_imm += 1  # num of calls answered immediately
            s.n_agents_talking += 1  # current number of Agents talking
            cust = Cust()  # create new cust object

            n_calls += 1

            s.ev_ia_time = ia_time_rand(s)
            s.ev_clock += s.ev_ia_time
            s.ev_type = EV.ARR
            s.ev_agent = agent_index
            s.ev_talk_time_proj = talk_time_rand(s)  # talk time projected for arriving call
            s.ev_abn_time_proj = abn_time_rand(s)  # abn time projected for arriving queued call

            cell_rc = cell_rc_from_cell_index(s, cell_index)
            qsp.cir_init(cust, cell_rc)  # populate cell and cir fields

            # cust.id_call = s.id_call
            cust.ev_clock = s.ev_clock
            cust.ev_ia_time = s.ev_ia_time
            cust.ev_type = s.ev_type
            cust.ev_agent = s.ev_agent
            cust.ev_talk_time_proj = s.ev_talk_time_proj
            cust.ev_abn_time_proj = s.ev_abn_time_proj

            cust.t_arr = s.ev_clock
            cust.t_ser = s.ev_clock
            cust.t_dep = 0
            cust.state = CS.ANS_IMM

            cust.agent = agent_index

            # create departure event
            dep_time_proj = cust.t_ser + cust.ev_talk_time_proj
            events.append([dep_time_proj, cust.ev_ia_time, EV.DEP, s.ev_agent,
                           cust.ev_talk_time_proj, cust.ev_abn_time_proj])

            call_data_update(s, cell_index, cust)

            # ----------------------
            qsl.event_new_log_row(s, cust, debug=s.debug_test)
            # ----------------------

        else:
            call_data_update(s, cell_index, cust=None, state='IDLE')

    pass

    for cell_index in range(r.QSLOT01, r.QSLOT16 + 1):
        n_in_q = s.dfs.iat[cell_index, c.CELL_MOD]
        if n_in_q <= n_calls_q:
            s.n_arr += 1  # num of calls arrived
            s.n_dly += 1  # num of calls entering Q (total)
            s.n_queued_calls += 1  # current number of calls in Q

            cust = Cust()

            cell_rc = cell_rc_from_cell_index(s, cell_index)
            qsp.cir_init(cust, cell_rc)  # populate cell and cir fields

            s.ev_ia_time = ia_time_rand(s)
            s.ev_clock += s.ev_ia_time
            s.ev_talk_time_proj = talk_time_rand(s)
            s.ev_abn_time_proj = abn_time_rand(s)
            s.ev_agent = 0

            cust.ev_clock = s.ev_clock
            cust.ev_ia_time = s.ev_ia_time
            cust.ev_type = EV.ARR
            cust.ev_agent = 0
            cust.ev_talk_time_proj = s.ev_talk_time_proj  # talk time projected for arriving call
            cust.abn_time_proj = s.ev_abn_time_proj  # abn time projected for arriving call

            # cust.id_call = s.id_call
            cust.t_arr = s.ev_clock
            cust.t_ser = 0
            cust.t_dep = 0
            cust.state = CS.IN_Q

            call_data_update(s, cell_index, cust)
            # ----------------------
            qsl.event_new_log_row(s, cust, debug=s.debug_test)
            # ----------------------

        else:
            call_data_update(s, cell_index, cust=None, state='IDLE')

        pass

    s.calls_in_system = n_calls

    if s.calls_in_system > 0:
        s.ev_clock *= 1.5  # give time for all pending departures to clear
        s.ev_clock = round(s.ev_clock, s.event_precision)

        # rebuild events()
        ia_time = ia_time_rand(s)
        next_arrival = round(s.ev_clock + ia_time, s.event_precision)
        event_ = [next_arrival, ia_time, EV.ARR, 0, talk_time_rand(s), abn_time_rand(s)]
        events.append(event_)
        events_all.append(event_)
        events_add_arr(s)
        events_sort(s)
        events_display(s, debug=1)

    return


def call_data_update(s, cell_index, cust, **kwargs):
    """updates dfs"""

    if 'state' in kwargs:
        state = kwargs['state']
        if state == 'IDLE':
            s.dfs.iat[cell_index, c.ID_CALL] = 0
            s.dfs.iat[cell_index, c.STATUS] = r.CELL_IDLE
            s.dfs.iat[cell_index, c.CUST] = None
            pass
        else:
            s.dfs.iat[cell_index, c.ID_CALL] = 0
            s.dfs.iat[cell_index, c.STATUS] = None
            s.dfs.iat[cell_index, c.CUST] = None
    elif 'reset' in kwargs:
        s.dfs.iat[cell_index, c.ID_CALL] = 0
        s.dfs.iat[cell_index, c.STATUS] = r.CELL_IDLE
        s.dfs.iat[cell_index, c.CUST] = None
    else:
        s.dfs.iat[cell_index, c.ID_CALL] = cust.id_call
        s.dfs.iat[cell_index, c.STATUS] = cust.state
        s.dfs.iat[cell_index, c.CUST] = cust
    pass
    return


# def call_data_update(s, cell_index, **kwargs):
#     """updates dfs"""
#     if 'reset' in kwargs:
#         s.dfs.iat[cell_index, c.ID_CALL] = 0
#         s.dfs.iat[cell_index, c.T_ARRIVAL] = 0
#         s.dfs.iat[cell_index, c.T_SERVICED] = 0
#         s.dfs.iat[cell_index, c.T_DEPARTURE] = 0
#         s.dfs.iat[cell_index, c.TIME_IN_Q] = 0
#         s.dfs.iat[cell_index, c.TIME_IN_SERVICE] = 0
#         s.dfs.iat[cell_index, c.STATUS] = None
#         s.dfs.iat[cell_index, c.CUST] = None
#     else:
#         if 'id_call' in kwargs:
#             s.dfs.iat[cell_index, c.ID_CALL] = kwargs['id_call']
#         if 't_arrival' in kwargs:
#             s.dfs.iat[cell_index, c.T_ARRIVAL] = kwargs['t_arrival']
#         if 't_serviced' in kwargs:
#             s.dfs.iat[cell_index, c.T_SERVICED] = kwargs['t_serviced']
#         if 't_departure' in kwargs:
#             s.dfs.iat[cell_index, c.T_DEPARTURE] = kwargs['t_departure']
#         if 'time_in_q' in kwargs:
#             s.dfs.iat[cell_index, c.TIME_IN_Q] = kwargs['time_in_q']
#         if 'time_in_service' in kwargs:
#             s.dfs.iat[cell_index, c.TIME_IN_SERVICE] = kwargs['time_in_service']
#         if 'status' in kwargs:
#             s.dfs.iat[cell_index, c.STATUS] = kwargs['status']
#         if 'cust' in kwargs:
#             s.dfs.iat[cell_index, c.CUST] = kwargs['cust']
#     return


def call_remove_from_q(s, cycle_time=1, debug=0):
    """moves call from head of Q to QSLOT00 - shifts remains queued calls returns cust"""
    if s.plot_flag > 0:
        qsp.call_remove_from_q_animate(s, cycle_time=s.cycle_time, debug=0)
        # for i_tick in range(0, 17):
        #     # update new_x/New_y
        #     s.dfcomb['new_x'] = s.dfcomb.iloc[:, c.X0 + i_tick]
        #     s.dfcomb['new_y'] = s.dfcomb.iloc[:, c.Y0 + i_tick]
        #
        #     for i_comb in range(r.QSLOT01, r.QSLOT16 + 1):  # dfcomb has same number of rows as dfs
        #         cust_ = s.dfs.iat[i_comb, c.CUST]
        #         if not isinstance(cust_,Cust):  #  np.isnan(cust_) or (cust_ is None):
        #             # no more queued calls
        #             break
        #         if isinstance(cust_.cir, plt.Circle):  # cir is not None:
        #             new_x = s.dfcomb.iat[i_comb, c.NEW_X]
        #             new_y = s.dfcomb.iat[i_comb, c.NEW_Y]
        #             # print(i_comb,i_tick,new_x,new_y)
        #             pass
        #             cust_.cir.center = (new_x, new_y)
        #         else:
        #             break
        #
        #         pass
        #     plt.pause(cycle_time / 1000)

    pass

    for i_system in range(r.QSLOT01, r.QSLOT16 + 1):
        cust_ = s.dfs.iloc[i_system, c.CUST]
        if isinstance(cust_, Cust):
            cust_.qslot -= 1
            s.dfs.iloc[i_system - 1, c.ID_CALL] = s.dfs.iloc[i_system, c.ID_CALL]
            s.dfs.iloc[i_system - 1, c.CUST] = cust_
            s.dfs.iloc[i_system - 1, c.STATUS] = s.dfs.iloc[i_system, c.STATUS]
            if i_system == r.QSLOT16:
                # clear top slot
                call_data_update(s, i_system, cust=None, reset=1)

        else:
            s.dfs.iloc[i_system - 1, c.ID_CALL] = 0
            s.dfs.iloc[i_system - 1, c.CUST] = None
            s.dfs.iloc[i_system - 1, c.STATUS] = r.CELL_IDLE
        pass
    pass

    if s.dfs.iloc[r.QSLOT01, c.STATUS] == r.CELL_IDLE:
        pass

    # clear QSLOTS00 holding cell
    call_data_update(s, r.QSLOT00, cust=None, reset=1)

    return


def display_dfs(s, i_system=0, debug=0):
    """displays dfs for debugging"""
    if debug > 0:
        if i_system == 0:  # all A/Q rows
            display(s.dfs.iloc[27:32, [0, 1, 5, 6, 7]])
            display(s.dfs.iloc[3:19, [0, 1, 5, 6, 7]])
        else:
            display(s.dfs.iloc[i_system, [0, 1, 5, 6, 7]])

    return


def events_to_excel(excel_file):
    with pd.ExcelWriter(excel_file, mode='a') as writer:
        events_df.to_excel(writer, sheet_name='events')
    with pd.ExcelWriter(excel_file, mode='a') as writer:
        events_all_df.to_excel(writer, sheet_name='events_all')
    return


def plot_active_callers(s):
    """plots active calls specified by initial conditions"""
    for i in range(1, s.n_agents_max + s.n_qslots_max + 1):
        id_call = s.dfs.at[i, c.ID_CALL]
        if id_call > 0:
            # cell_rc_initial = cell_rc_from_cell_index(s, r.NEWCALL0)
            # cust.cir = qsp.cir_init(cust, cell_rc_initial)

            cust = Cust()
            cell_rc = cell_rc_from_cell_index(s, i)
            # ---------------
            cust.cir = qsp.cir_init(cust, cell_rc)
            qsp.cir_plot(s, cust.cir)
            # ---------------
            s.dfs.at[i, 'cust'] = cust.cir

    return

#     """
#         from iterrows() in manual
#         --------------------------
#         You should **never modify** something you are iterating over.
#             This is not guaranteed to work in all cases.
#             Depending on the data types,
#                 the iterator returns a copy and not a view,
#                 and writing to it will have no effect.
#         -----------------------------
#         seems to be ok, but I moved to using indexs to be safe
#         """
# pass
# -----------
