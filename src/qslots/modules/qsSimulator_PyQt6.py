# from config import *
import matplotlib
from matplotlib import pyplot as plt
import datetime as dt

import pandas as pd
import numpy as np

from app.modules import qsTests, qsDataframes, qsPlot

# import modules\qsDataframes as qsd
# import modules\qsTests as qst
# import modules\qsPlot as qsp

matplotlib.use('TkAgg')
plt.ion()


class QSlotSimulation:
    def __init__(self):
        self.debug = 0
        self.debug_test = 0
        self.debug_calls = 0
        self.plot_flag = 1
        self.debug_dfs = 0
        self.cycle_time = 1  # for animation

        self.n_agents_max = 8
        self.n_qslots_max = 16
        self.n_agents_sim = 5  # max number of agents in simulation
        self.n_qslots_sim = 16  # max number of QSlots in simulation

        self.arrival_rate_av = 240.0  # calls per hour
        self.talk_time_av = 60.0  # service time in seconds
        self.arrival_boost = 1.1
        self.erl = self.arrival_rate_av * self.talk_time_av / 3600  # traffic in Erlangs
        self.inter_arrival_time_av = 3600 / self.arrival_rate_av  # seconds
        self.delay_test_time = 30.0  # number of calls delayed greater than T seconds
        self.abn_time_av = 0.0  # mean wait before queued call abandons
        self.event_precision = 4  # for random number of timing events

        # working variables
        self.clock = 0.0  # current clock
        self.next_free_agent = 0
        self.next_free_qslot = 0
        self.t_highest_arr_time_in_events = 0.0
        self.t_future_dep_time = 0.0
        self.t_future_abn_time = 0.0
        self.agent_leaving = 0
        self.t_arr_original = 0.0  # used for delayed calls

        # log items
        self.ev_clock = 0.0  # sim clock
        self.ev_ia_time = 0.0  # ia_time to this event
        self.ev_type = 0  # new event -0=arr 1=dep 2=queue call abandoned
        self.ev_agent = 0  # new event -ev_agent index for departing call
        self.ev_talk_time_proj = 0.0  # new event -talk time projected for arriving call
        self.ev_abn_time_proj = 0.0  # new event -abandon time projected for queued call

        self.id_call = 0  # id_call - auto incremented	for each new call
        self.id_call_current = 0  # id_call of call leaving Q or ev_agent - for log
        self.call_state = 0  # call state
        self.completed = 0  # completed flag

        self.t_arr = 0.0  # clock time -call arrived
        self.t_abn = 0.0  # clock time -call abandoned
        self.t_ser = 0.0  # clock time -call answered
        self.t_dep = 0.0  # clock time -call leaves agent
        self.t_dep_latest = 0.0  # needed for t_ser of queued call takig place of depating caal

        self.wait_time = 0.0  # wait time duration
        self.talk_time = 0.0  # talk time duration
        self.abn_time = 0.0  # time to abandonment

        # current state
        self.n_agents_talking = 0  # current number of Agents talking
        self.n_queued_calls = 0  # current number of calls in Q

        # running totals
        self.n_arr = 0  # num of calls arrived
        self.n_blk_imm = 0  # num of calls blocked (Q full)
        self.n_abn_imm = 0  # num of calls abandoning if no ev_agent immediately available
        self.n_abn_dly = 0  # num of calls abandoning after spending some time in Q
        self.n_dly = 0  # num of calls entering Q (total)
        self.n_dly_t = 0  # num of calls entering Q whose delay before answer less than T seconds
        self.n_ans_imm = 0  # num of calls answered immediately
        self.n_ans_dly = 0  # num of calls answered who had been delayed
        self.n_dep = 0  # num of calls leaving (all reasons)
        self.n_dep_imm = 0  # num of calls leaving agent having been imm answered
        self.n_dep_dly = 0  # num of calls leaving agent having been delayed

        # n_arr=n_ans_imm+n_dly+n_abn_imm+n_blk_imm
        # n_dly=n_abn_dly+n_ans_dly
        # nDep=n_arr+n_abn_imm+n_blk_imm

        self.events = []  # empty list
        self.event_log_row = {}  # individual log record (dictionary)
        self.events_log_df = pd.DataFrame()

        self.textprops = None

        self.today = ''
        self.today_time = ''
        self.excel_file = ''
        self.excel_sheet = ''

        self.timer_start = 0.0
        self.timer_end = 0.0
        self.event = 'new'
        self.event_clock_td = dt.timedelta(0)
        self.event_clock_td_1 = dt.timedelta(0)

        self.dfs = None
        self.dfp = None
        self.dff = None
        self.dfcomb = None
        self.eventsdf = None
        self.plot = None

        pass


# -------------------------------
def main():
    s = QSlotSimulation()

    s.n_agents_max = 8
    s.n_qslots_max = 16
    s.n_agents_sim = 5  # max number of agents in simulation
    s.n_qslots_sim = 16  # max number of QSlots in simulation

    n_calls_a = 0
    n_calls_q = 0
    n_events = 100000

    s.debug = 0
    s.debug_test = 0
    s.debug_calls = 0
    s.plot_flag = 1
    s.debug_dfs = 0
    s.cycle_time = 0.1

    s.arrival_rate_av = 290.0  # calls per hour
    s.talk_time_av = 60.0  # service time in seconds
    s.erl = s.arrival_rate_av * s.talk_time_av / 3600  # traffic in Erlangs

    s.arrival_boost = 1.5

    s.inter_arrival_time_av = 3600 / s.arrival_rate_av  # seconds
    s.delay_test_time = 30.0  # number of calls delayed greater than T seconds
    s.abn_time_av = 0.0  # mean wait before queued call abandons
    s.event_precision = 4  # for random number of timing events

    s.next_free_agent = 0
    s.next_free_qslot = 0
    s.t_highest_arr_time_in_events = 0.0
    s.t_future_dep_time = 0.0
    s.t_future_abn_time = 0.0

    # log items
    s.log_index = 0  # events_log_df index
    s.ev_clock = 0.0  # new event -clock time
    s.ev_ia_time = 0.0  # ia_time to this event
    s.ev_type = 0  # new event -0=arr 1=dep
    s.ev_agent = 0  # new event -ev_agent index for departing call
    s.ev_talk_time_proj = 0.0  # new event -talk time projected for arriving call
    s.ev_abn_time_proj = 0.0  # new event -abandon wait time projected for queued call

    s.id_call = 0  # global used to provide sequential ID to each new call
    s.call_state = ''  # call status
    s.completed = 0  # completed flag
    #   1   completed with no delay
    #   2   completed with delat <=service time
    #   3   completed with delay > service time
    #   4   abandoned before answer
    #   5   blocked (queue full)
    #   0   still in prgress

    # s.iD_existingCall = 0  # id_call of call leaving Q or ev_agent - for log

    s.t_arr = 0.0  # clock time -call arrived
    s.t_abn = 0.0  # clock time -call abandoned
    s.t_ser = 0.0  # clock time -call answered
    s.t_dep = 0.0  # clock time -call leaves ev_agent
    s.t_dep_latest = 0.0  # needed for t_ser of queued call takig place of depating caal

    s.wait_time = 0.0  # wait time duration
    s.talk_time = 0.0  # talk time duration
    s.abn_time = 0.0  # time to abandonment

    # current state
    s.n_agents_talking = 0  # current number of Agents talking
    s.n_queued_calls = 0  # current number of calls in Q

    # running totals
    s.n_arr = 0  # num of calls arrived
    s.n_blk_imm = 0  # num of calls blocked (Q full)
    s.n_abn_imm = 0  # num of calls abandoning if no ev_agent immediately available
    s.n_abn_dly = 0  # num of calls abandoning after spending some time in Q

    s.n_dly = 0  # num of calls entering Q (total)
    s.n_dly_t = 0  # num of calls entering Q whose delay before answer exceeds T seconds
    s.n_ans_imm = 0  # num of calls answered immediately
    s.n_ans_dly = 0  # num of calls answered who had been delayed
    s.n_dep = 0  # num of calls leaving (all reasons)
    s.n_dep_imm = 0  # num of calls leaving agent having been imm answered
    s.n_dep_dly = 0  # num of calls leaving agent having been delayed

    s.textprops = dict(color='k', fontsize=18, fontweight='bold')

    qsd.import_dataframes(s, debug=s.debug)
    if s.plot_flag > 0:
        s.plot = qsp.plot_create(s)
        qsp.plot_add_frame(s, n_agents_max=s.n_agents_sim, n_qslots_max=s.n_qslots_sim, debug=s.plot_flag)

    pass
    # for debugging
    s.eventsdf = pd.DataFrame(columns=['ev_clock', 'ev_type', 'agent', 'talk_time', 'abn_Time'])

    qst.test_full(s, n_calls_a, n_calls_q, n_events, debug=s.debug_test)

    if s.plot_flag > 0:
        plt.show(block=True)

    pass
    return


# ---------------------------


if __name__ == "__main__":
    main()

pass

pass
