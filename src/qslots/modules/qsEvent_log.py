import os

import pandas as pd
import datetime as dt
import numpy as np
import openpyxl

from cust import CS, EV  # Cust state , Event type
import infobox as qsi

import qsControl as qscont


# module level variables
event_log_row0 = {}
event_log_row1 = {}
events_log_df = pd.DataFrame()

ags_s = 0.0  # running total  'ags_'
q_s = 0.0  # running total  'q_'

pimm = 0.0  # prob imm ans
pdly_ltt = 0.0  # prob delay <=Y
pdly_gtt = 0.0  # prob delay >T
pblk = 0.0  # prob blocked (queue full)
pabn = 0.0  # prob aban before ans
psl = 0.0  # service level (pimm+pdly_ltt)

talk_av = 0.0  # talk average (completed calls)
asa_dly_av = 0.0  # asa delayed calls
asa_av = 0.0  # asa all serviced calls (excludes abans and blocked)
abn_av = 0.0  # abandon time av

n_comp_imm = 0  # completed calls answered imm
n_comp_ltt = 0  # completed calls delayed <=T
n_comp_gtt = 0  # completed calls delayed >T
n_comp_abn = 0  # calls abandoned before ans
n_comp_blk = 0  # calls blocked (queue full)
n_comp_tot = 0  # total completed calls (including calls blocked)

talk_s = 0  # talk time running total
wait_s = 0  # wait time running total
abn_s = 0  # aban time running total


def event_new_log_row(s, cust, debug=0, reset=0):
    """
    loads log items into a df and concatenates this to cust.events_log_df
    reset=1     creates initial dfs and empty cust.events_log_df
    debug=1     display cust.events_log_df.tail(displayRows)
    """
    global events_log_df, event_log_row0, event_log_row1
    global ags_s, q_s
    global n_comp_imm, n_comp_ltt, n_comp_gtt, n_comp_abn, n_comp_blk, n_comp_tot
    global pimm, pdly_ltt, pdly_gtt, pblk, pabn, psl
    global talk_s, wait_s, abn_s, talk_av, asa_dly_av, asa_av

    if reset > 0:
        s.log_index = 0

        td0 = dt.timedelta(0)
        # t0 = 0.0  # secs_to_timedelta(0.0)
        s.event_clock_td_1 = td0  # prior event time
        s.study_clock_td = td0
        event_log_row0 = {
            'index': [s.log_index],
            'time_hrs': [0.0],
            'n_agents_talking': [0.0],
            'n_queued_calls': [0.0],
            'n_system_calls': [0.0],
            'ags_av': [0.0],  # average 'n_agents_talking'
            'q_av': [0.0],  # averagr 'n_queued_calls'

            'pimm': [0.0],  # prob imm ans
            'pdly_ltt': [0.0],  # prob delay <=Y
            'pdly_gtt': [0.0],  # prob delay >T
            'pblk': [0.0],  # prob blocked (queue full)
            'pabn': [0.0],  # prob aban before ans
            'psl': [0.0],  # service level (pimm+pdly_ltt)

            'talk_av': [0.0],  # talk average (completed calls)
            'asa_dly_av': [0.0],  # asa delayed calls
            'asa_av': [0.0],  # asa all serviced calls (excludes abans and blocked)
            'abn_av': [0.0],  # abandon time av

            'n_comp_imm': [0],  # completed calls answered imm
            'n_comp_ltt': [0],  # completed calls delayed <=T
            'n_comp_gtt': [0],  # completed calls delayed >T
            'n_comp_abn': [0],  # calls abandoned before ans
            'n_comp_blk': [0],  # calls blocked (queue full)
            'n_comp_tot': [0],  # total completed calls (including calls blocked)

            'talk_s': [0.0],  # talk time running total
            'wait_s': [0.0],  # wait time running total
            'abn_s': [0.0],  # aban time running total

            'dt': [0.0],
            'ags_': [0.0],  # 'n_agents_talking' * 'dt'
            'q_': [0.0],  # 'n_queued_calls' * 'dt'
            'ags_s': [0.0],  # running total  'ags_'
            'q_s': [0.0],  # running total  'q_'

            'hour': [0.0],

            'study_clock_td': [td0],
            'event_clock': [0.0],
            'event_clock_td': [td0],
            'event_clock_td_str': ['000:00:00'],
            'event': ['start'],
            'event_mod': [''],
            'agent_index': [0],
            'qslot_index': [0],

            'ev_clock': [0.0],
            'ev_type': ['arr'],  # first record
            'ev_ia_time': [0.0],
            'ev_agent': [0],
            'ev_talk_time_proj': [0.0],
            'ev_abn_time_proj': [0.0],

            'id_call': [0],
            'call_state': ['idle'],
            'completed': [0],

            't_arr': [0.0],
            't_abn': [0.0],
            't_ser': [0.0],
            't_dep': [0.0],

            'wait_time': [0.0],
            'talk_time': [0.0],
            'abn_time': [0.0],

            'n_arr': [0],
            'n_blk_imm': [0],
            'n_abn_imm': [0],
            'n_abn_dly': [0],

            'n_dly': [0],
            'n_dly_t': [0],
            'n_ans_imm': [0],
            'n_ans_dly': [0],
            'n_dep': [0]
        }
    else:
        s.log_index += 1
        study_clock_td = dt.datetime.now() - s.timer_start
        dur = round(study_clock_td.total_seconds(), s.event_precision)
        l_event_str = ''
        l_event_mod_str = ''
        t_adj = 0.0

        match cust.state:
            case CS.NEW:
                l_event_str = "New"
                l_event_mod_str = "Call"
                t_adj = cust.t_arr
            case CS.ANS_IMM:
                l_event_str = "Ans"
                l_event_mod_str = f"imm by agent {cust.agent}"
                t_adj = cust.t_arr
            case CS.ANS_DELAY:
                l_event_str = "Ans"
                l_event_mod_str = "after delay"
                # cust.t_ser=s.t_dep_last
                t_adj = cust.t_ser
            case CS.IN_Q:
                l_event_str = "Queued"
                l_event_mod_str = f"to Q slot {cust.qslot}"
                t_adj = cust.t_arr
            case CS.LEAVE_Q:
                l_event_str = "Leave Q"
                l_event_mod_str = f"to agent {cust.agent}"
                t_adj = cust.t_ser
            case CS.IMM_BLOCK:
                l_event_str = "Blocked"
                l_event_mod_str = "Q full"
                t_adj = cust.t_arr
            case CS.COMPLETED_DLY_LTT:
                l_event_str = "Departed"
                l_event_mod_str = f"dly<{s.delay_test_time:0n}"
                t_adj = cust.t_dep
            case CS.COMPLETED_DLY_GTT:
                l_event_str = "Departed"
                l_event_mod_str = f"dly>{s.delay_test_time:0n}"
                t_adj = cust.t_dep
            case CS.COMPLETED_ABN:
                l_event_str = "Departed"
                l_event_mod_str = "abandoned"
                t_adj = cust.t_dep
            case CS.COMPLETED_IMM:
                l_event_str = "Departed"
                l_event_mod_str = "after imm ans"
                t_adj = cust.t_dep
            case _:
                l_event_str = "???"
                l_event_mod_str = "???"
                t_adj = cust.t_dep

        # import datetime as dt
        # hrs = 34
        # mins = 30
        # secs = 45
        # ms = 670
        #
        # t_adj_ms = 1000 * (secs + 60 * (mins + 60 * hrs))
        #
        # event_clock_adj = dt.timedelta(milliseconds=t_adj_ms)
        # t_adj_ms_1 = round(t_adj_ms - 8780 - 1000 / 3, 2)
        # event_clock_adj_1 = dt.timedelta(milliseconds=t_adj_ms_1)
        # pass
        # dt_ = event_clock_adj - event_clock_adj_1  # underscore to avoid dt as datetime alias
        # dt_.resolution
        #
        # # get min and seconds first
        # mm, ss = divmod(t_adj_ms / 1000, 60)
        # # # Get hours
        # hh, mm = divmod(mm, 60)
        # t_adj_str = f"{hh:.0f}: {mm:.0f}: {ss:.0f}"
        # print(t_adj_str)

        event_clock = t_adj
        event_clock_td = dt.timedelta(milliseconds=1000*round(t_adj,s.event_precision))
        mm, ss = divmod(t_adj, 60)
        ss = round(ss, 0)
        # Get hours
        hh, mm = divmod(mm, 60)
        hh = round(hh, 0)
        # f'{my_num:{".2f" if my_bool else ""}}
        if hh==0:
            event_clock_td_str = f"{mm:0>2n}:{ss:0>2n}"
        else:
            event_clock_td_str = f"{hh:0>3n}:{mm:0>2n}:{ss:0>2n}"

        dt_ = (event_clock_td - s.event_clock_td_1).total_seconds()  # underscore to avoid dt as datetime alias
        s.event_clock_td_1 = event_clock_td

        l_ev_type = ''
        match cust.ev_type:
            case EV.SKIP:
                l_ev_type = "skip"
            case EV.ARR:
                l_ev_type = "arr"
            case EV.DEP:
                l_ev_type = "dep"
            case _:
                l_ev_type = "???"

        event_log_row_load_chart_fields(cust)

        event_log_row1 = {
            'index': [s.log_index],
            'time_hrs': [round(t_adj / 3600, s.event_precision)],
            'n_agents_talking': [float(s.n_agents_talking)],  # fill_between gets upset with ints
            'n_queued_calls': [float(s.n_queued_calls)],
            'n_system_calls': [float(s.n_agents_talking + s.n_queued_calls)],
            'ags_av': [0.0],  # average 'n_agents_talking'
            'q_av': [0.0],  # averagr 'n_queued_calls'

            'pimm': [pimm],  # prob imm ans
            'pdly_ltt': [pdly_ltt],  # prob delay <=Y
            'pdly_gtt': [pdly_gtt],  # prob delay >T
            'pblk': [pblk],  # prob blocked (queue full)
            'pabn': [pabn],  # prob aban before ans
            'psl': [psl],  # service level (pimm+pdly_ltt)

            'talk_av': [talk_av],  # talk average (completed calls)
            'asa_dly_av': [asa_dly_av],  # asa delayed calls
            'asa_av': [asa_av],  # asa all serviced calls (excludes abans and blocked)
            'abn_av': [abn_av],  # abandon time av

            'n_comp_imm': [n_comp_imm],  # completed calls answered imm
            'n_comp_ltt': [n_comp_ltt],  # completed calls delayed <=T
            'n_comp_gtt': [n_comp_gtt],  # completed calls delayed >T
            'n_comp_abn': [n_comp_abn],  # calls abandoned before ans
            'n_comp_blk': [n_comp_blk],  # calls blocked (queue full)
            'n_comp_tot': [n_comp_tot],  # total completed calls (including calls blocked)

            'talk_s': [talk_s],  # talk time running total
            'wait_s': [wait_s],  # wait time running total
            'abn_s': [abn_s],  # aban time running total

            'dt': [0.0],
            'ags_': [0.0],  # 'n_agents_talking' * 'dt'
            'q_': [0.0],  # 'n_queued_calls' * 'dt'
            'ags_s': [0.0],  # running total  'ags_'
            'q_s': [0.0],  # running total  'q_',

            'hour': [int(t_adj / 3600.0)],

            'study_clock_td': [study_clock_td],
            'event_clock': [t_adj],
            'event_clock_td': [event_clock_td],
            'event_clock_td_str': [event_clock_td_str],
            'event': [l_event_str],
            'event_mod': [l_event_mod_str],
            'agent_index': [cust.agent],
            'qslot_index': [cust.qslot],

            'ev_clock': [cust.ev_clock],
            'ev_type': [l_ev_type],
            'ev_ia_time': [cust.ev_ia_time],
            'ev_agent': [cust.ev_agent],
            'ev_talk_time_proj': [cust.ev_talk_time_proj],
            'ev_abn_time_proj': [cust.ev_abn_time_proj],

            'id_call': [cust.id_call],
            'call_state': [l_event_str],
            'completed': [cust.completed],

            't_arr': [cust.t_arr],
            't_abn': [cust.t_abn],
            't_ser': [cust.t_ser],
            't_dep': [cust.t_dep],

            'wait_time': [cust.wait_time],
            'talk_time': [cust.talk_time],
            'abn_time': [cust.abn_time],

            'n_arr': [s.n_arr],
            'n_blk_imm': [s.n_blk_imm],
            'n_abn_imm': [s.n_abn_imm],
            'n_abn_dly': [s.n_abn_dly],

            'n_dly': [s.n_dly],
            'n_dly_t': [s.n_dly_t],
            'n_ans_imm': [s.n_ans_imm],
            'n_ans_dly': [s.n_ans_dly],
            'n_dep': [s.n_dep]
        }
        # ---------update event_log_row0
        # _dt_col = events_log_df.columns.get_loc('dt')
        # events_log_df.iloc[-1,events_log_df.columns.get_loc('dt')] =dt_

        n_ags = event_log_row0['n_agents_talking'][0]
        n_q = event_log_row0['n_queued_calls'][0]
        ags_ = n_ags * dt_
        q_ = n_q * dt_

        ags_s += ags_  # running total  'ags_'
        q_s += q_  # running total  'q_'

        if t_adj > 0:
            ags_av = ags_s / t_adj  # average 'n_agents_talking'
            q_av = q_s / t_adj  # averagr 'n_queued_calls'
        else:
            ags_av = 0.0
            q_av = 0.0

        event_log_row0.update(
            {
                'dt': [dt_],
                'ags_': [ags_],
                'q_': [q_],
                'ags_s': [ags_s],
                'q_s': [q_s],
                'ags_av': [ags_av],
                'q_av': [q_av]
            })

        if np.isclose(dt_, 0):
            # remove transient event combination when agent complates a call and
            # a queued call immwdiatly takes its place (poor agent)
            #       n_ags   n_queued    n_system
            # row0  5       1           6
            # row1  4       1           5        <- transient state dt=0
            # row2  5       0           5

            # replace row 1 values with row0

            n_ags = event_log_row1['n_agents_talking'][0]
            n_q = event_log_row1['n_queued_calls'][0]

            event_log_row0.update(
                {
                    'n_agents_talking': n_ags,
                    'n_queued_calls': n_q,
                    'n_system_calls': n_ags + n_q
                })

        df0 = pd.DataFrame.from_dict(event_log_row0)
        events_log_df = pd.concat([events_log_df, df0])
        # if s.log_index==1:
        #     events_log_df.set_index('index', inplace=True)
        event_log_row0 = event_log_row1

        if s.plot_flag > 0:
            df1 = pd.DataFrame.from_dict(event_log_row1)
            qsi.infobox_update(s, df1)
            qscont.qscontrol(s.ievent)

        pass

    pass
    return event_log_row0  # needed for infobox_init


def event_log_row_load_chart_fields(cust):
    global n_comp_imm, n_comp_ltt, n_comp_gtt, n_comp_abn, n_comp_blk, n_comp_tot
    global talk_s, wait_s, abn_s, talk_av, asa_dly_av, asa_av
    global pimm, pdly_ltt, pdly_gtt, pblk, pabn, psl

    match cust.completed:
        case 0:
            pass
        case 1:
            n_comp_imm += 1  # completed calls answered imm
            n_comp_tot += 1  # total completed calls (including calls blocked)
        case 2:
            n_comp_ltt += 1  # completed calls delayed <=T
            n_comp_tot += 1  # total completed calls (including calls blocked)
        case 3:
            n_comp_gtt += 1  # completed calls delayed >T
            n_comp_tot += 1  # total completed calls (including calls blocked)
        case 4:
            n_comp_abn += 1  # calls abandoned before ans
            n_comp_tot += 1  # total completed calls (including calls blocked)
        case 5:
            n_comp_blk += 1  # calls blocked (queue full)
            n_comp_tot += 1  # total completed calls (including calls blocked)
        case _:
            pass

    if n_comp_tot > 0:
        pimm = n_comp_imm / n_comp_tot  # prob imm ans
        pdly_ltt = n_comp_ltt / n_comp_tot  # prob delay <=Y
        pdly_gtt = n_comp_gtt / n_comp_tot  # prob delay >T
        pabn = n_comp_abn / n_comp_tot  # prob aban before ans
        pblk = n_comp_blk / n_comp_tot  # prob blocked (queue full)
        psl = pimm + pdly_ltt  # service level (pimm+pdly_ltt)

    if cust.ev_type == EV.DEP:
        talk_s += cust.talk_time  # talk time running total
        wait_s += cust.wait_time  # wait time running total
        abn_s += cust.abn_time  # aban time running total

    n_comp_answered = n_comp_imm + n_comp_ltt + n_comp_gtt
    if n_comp_answered > 0:
        talk_av = talk_s / n_comp_answered  # talk average (completed calls)

    n_comp_dly = n_comp_ltt + n_comp_gtt
    if n_comp_dly > 0:
        asa_dly_av = wait_s / n_comp_dly  # asa delayed calls
        asa_av = wait_s / n_comp_answered  # asa all serviced calls (excludes abans and blocked)

    if n_comp_abn > 0:
        abn_av = abn_s / n_comp_abn  # abandon time av

    return


def events_log_to_excel(s, excel_file, sheet_name='today'):
    # events_display(s, debug=1)

    # # Write to Multiple Sheets
    # df2 = df.clone()
    # with pd.ExcelWriter('Courses.xlsx') as writer:
    #     df.to_excel(writer, sheet_name='Technologies')
    #     df2.to_excel(writer, sheet_name='Schedule')

    # # Append DataFrame to existing excel file
    # with pd.ExcelWriter('Courses.xlsx', mode='a') as writer:
    #     df.to_excel(writer, sheet_name='Technologies')

    if os.path.exists(excel_file):
        os.remove(excel_file)

    with pd.ExcelWriter(excel_file) as writer:
        events_log_df.to_excel(writer, sheet_name='log')

    with pd.ExcelWriter(excel_file, mode='a') as writer:
        s.dfs.to_excel(writer, sheet_name='system')

    # qsc.events_to_excel(excel_file)

    pass
    return


def events_to_pickle(pickle_file):
    if os.path.exists(pickle_file):
        os.remove(pickle_file)
    events_log_df.to_pickle(pickle_file)
    return


def main():
    pass


if __name__ == "__main__":
    main()

pass
