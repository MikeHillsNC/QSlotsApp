import qsCalls as qsc
import qsEvent_log as qsl
from cust import *

import qsConstantsDfcomb as c
import qsConstantsDfs as r
from qsSimulator import QSlotSimulation

s = QSlotSimulation()


def test_full_new(n_events=None):
    for s.ievent in range(n_events):

        # startup 10% boost of arrival rate
        if s.ievent <= 100:
            s.arrival_boost = 1.2
        else:
            s.arrival_boost = 1.0

        s.ev_clock, s.ev_ia_time, s.ev_type, s.ev_agent, s.ev_talk_time_proj, \
        s.ev_abn_time_proj = qsc.call_next_event(s, debug=s.debug_test)

        if s.ev_type == EV.SKIP:
            continue  # skip any null events

        s.completed = 0
        #   1   completed with no delay
        #   2   completed with delat <=service time
        #   3   completed with delay > service time
        #   4   abandoned before answer
        #   5   blocked (queue full)
        #   0   still in progress

        if s.ev_type == EV.ARR:
            # a new call is loaded into cell NEWCALL0
            # from there it will move to an agent/the q/blocked imm
            # see qslots.xlsx for diagram of cells
            # start list of r,c tuples describing path call will take

            # --------------
            cust = Cust()  # create new cust - auto assigns cust.id_call
            # --------------
            cust.ev_clock = s.ev_clock
            cust.ev_ia_time = s.ev_ia_time
            cust.ev_type = s.ev_type
            cust.ev_agent = s.ev_agent
            cust.talk_time_proj = s.ev_talk_time_proj  # talk time projected for arriving call
            cust.abn_time_proj = s.ev_abn_time_proj  # abn time projected for arriving call

            cust.t_arr = s.ev_clock
            # ------------------
            qsc.call_new(s, cust, cycle_time)
            # ------------------

            if cust.state == CS.COMPLETED_ABN:
                cust_departing = cust

                cust_departing.ev_clock = s.ev_clock
                cust_departing.ev_ia_time = s.ev_ia_time
                cust_departing.ev_type = s.ev_type
                cust_departing.ev_agent = s.ev_agent
                cust_departing.ev_talk_time_proj = s.ev_talk_time_proj  # talk time projected for arriving call
                cust_departing.abn_time_proj = s.ev_abn_time_proj  # abn time projected for arriving call

                cust_departing.t_dep = s.ev_clock
                cust_departing.talk_time = 0.0
                cust_departing.wait_time = 0.0
                agent_index = 0

                s.t_dep_latest = cust_departing.t_dep  # needed for t_ser of queued call taking place of departed call

                cust_departing.completed = 5
                #   1   completed with no delay
                #   2   completed with delat <=service time
                #   3   completed with delay > service time
                #   4   abandoned before answer
                #   5   blocked (queue full)
                #   0   still in prgress

                # TODO  check this case out

                # # ----------------------
                # # plot stuff
                # if s.plot_flag > 0:
                #     cell_rc_initial = qsc.cell_rc_from_cell_index(s, r.NEWCALL0)
                #     qsc.call_dep(s, cust_departing, cell_rc_initial, cycle_time=s.cycle_time)
                # # ----------------------

                # ----------------------
                # log call dep
                qsl.event_new_log_row(s, cust_departing, debug=s.debug_test)
                # ----------------------

                # ----------
                # update dfs departing call
                qsc.call_data_update(s, r.NEWCALL0, cust=None, state='IDLE')
                del cust_departing
                # ----------

        elif s.ev_type == EV.DEP:
            cust_departing = s.dfs.iat[r.AGENTS[s.ev_agent], c.CUST]
            cust_departing.ev_clock = s.ev_clock
            cust_departing.ev_ia_time = s.ev_ia_time
            cust_departing.ev_type = s.ev_type
            cust_departing.ev_agent = s.ev_agent
            cust_departing.ev_talk_time_proj = s.ev_talk_time_proj  # talk time projected for arriving call
            cust_departing.abn_time_proj = s.ev_abn_time_proj  # abn time projected for arriving call

            cust_departing.t_dep = s.ev_clock
            cust_departing.talk_time = cust_departing.t_dep - cust_departing.t_ser
            cust_departing.wait_time = cust_departing.t_ser - cust_departing.t_arr
            agent_index = cust_departing.agent

            s.t_dep_latest = cust_departing.t_dep  # needed for t_ser of queued call taking place of departed call

            if cust_departing.state == CS.ANS_IMM:
                cust_departing.completed = 1
                cust_departing.state = CS.COMPLETED_IMM
                s.n_dep += 1  # num of calls leaving (all reasons)
                s.n_dep_imm += 1  # num of calls leaving agent having been imm answered
                s.n_agents_talking -= 1  # current number of Agents talking
            else:

                if cust_departing.wait_time <= s.delay_test_time:
                    s.n_dly_t += 1
                    cust_departing.state = CS.COMPLETED_DLY_LTT
                    cust_departing.completed = 2
                else:
                    cust_departing.state = CS.COMPLETED_DLY_GTT
                    cust_departing.completed = 3

                s.n_dep += 1  # num of calls leaving (all reasons)
                s.n_dep_dly += 1  # num of calls leaving agent having been delayed
                s.n_agents_talking -= 1  # current number of Agents talking

            # ----------------------
            # log call dep
            qsl.event_new_log_row(s, cust_departing, debug=s.debug_test)
            # ----------------------

            # ----------------------
            # plot stuff
            qsc.call_dep(s, cust_departing, cust_departing.ev_agent, cycle_time=s.cycle_time)
            # ----------------------

            # ----------
            # update dfs departing call
            qsc.call_data_update(s, r.AGENTS[agent_index], cust=None, state='IDLE')
            del cust_departing
            # ----------

            # ----------------------------------------
            # is there a queued call to take its place
            # ----------------------------------------
            cust_from_q = s.dfs.iat[r.QSLOT01, c.CUST]
            if isinstance(cust_from_q, Cust):
                cust_from_q.agent = agent_index
                cust_from_q.cell_type = CT.AGENT
                cust_from_q.cell_mod = agent_index
                cust_from_q.t_ser = s.t_dep_latest  # dep time of latest departing call
                #  cust_from_q.ia_time = s.ev_ia_time existing cust_from_q.ia_time is fine
                cust_from_q.t_dep = cust_from_q.t_ser + cust_from_q.ev_talk_time_proj
                cust_from_q.wait_time = cust_from_q.t_ser - cust_from_q.t_arr
                # cust_from_q.time_in_q = cust_from_q.t_ser - cust_from_q.t_arr
                cust_from_q.state = CS.LEAVE_Q

                s.n_ans_dly += 1  # num of calls answered who had been delayed
                s.n_agents_talking += 1  # current number of Agents talking
                s.n_queued_calls -= 1  # current number of calls in Q

                # ----------------------
                # log call leaving Q
                qsl.event_new_log_row(s, cust_from_q, debug=s.debug_test)
                # ----------------------

                qsc.call_remove_from_q(s, cycle_time=s.cycle_time, debug=0)

                cust_from_q.state = CS.ANS_DELAY
                # ----------------------
                # log call delayed answer
                qsl.event_new_log_row(s, cust_from_q, debug=s.debug_test)
                # ----------------------

                qsc.call_q_to_a(s, cust_from_q, agent_index)

                # create departure event
                dep_event_ = [cust_from_q.t_dep, cust_from_q.ev_ia_time, EV.DEP, cust_from_q.agent,
                              cust_from_q.ev_talk_time_proj, 0.0]
                qsc.events.append(dep_event_)
                qsc.events_all.append(dep_event_)
                qsc.events_display(s, debug=s.debug_test)

                qsc.call_data_update(s, r.AGENTS[agent_index], cust_from_q)  # update dfs
                # qsl.event_new_log_row(s, cust_from_q, debug=s.debug_test)  # log Q to A event
                qsc.display_dfs(s, i_system=0, debug=s.debug_dfs)

                pass

            # if s.debug_test > 0 and (i%100==99):
            #     events_to_excel(s, s.excel_file, sheet_name=s.excel_sheet)

        pass  # for loop
