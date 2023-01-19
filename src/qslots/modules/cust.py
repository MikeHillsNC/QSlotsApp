from IPython.display import display
from enum import Enum

import qsPlot as qsp


# Call State
class CS(Enum):
    IDLE = 0  # 'not yet in system'
    NEW = 1
    IMM_BLOCK = 2  # 'Blocked'
    ANS_IMM = 3  # 'Talking immediate answer'
    IN_Q = 4  # 'In queue'
    IN_Q_T = 5  # 'In queue - longer than T seconds'
    ANS_DELAY = 6  # 'Talking after queuing'
    COMPLETED_ABN = 7  # 'Left system - abn'
    COMPLETED_DLY_LTT = 8  # 'Left system - dly<T'
    COMPLETED_DLY_GTT = 9  # 'Left system - dly>T'
    COMPLETED_IMM = 10  # 'Left system - imm ans'
    LEAVE_Q = 11  # 'Leave Q to agent'


# Cell Type
class CT(Enum):
    TEMP = 0  # Temp
    AGENT = 1  # Agent
    QSLOT = 2  # QSlot


# Event Type
class EV(Enum):
    SKIP = -1
    ARR = 0
    DEP = 1


class Cust:
    id_call = 0  # class variable

    def __init__(self):
        Cust.id_call += 1

        self.id_call = Cust.id_call  # id_call - auto incremented	for each new call

        self.ev_clock = 0.0
        self.ev_type = EV.SKIP
        self.ev_agent = 0
        self.ev_talk_time_proj = 0.0  # talk time projected for arriving call
        self.ev_abn_time_proj = 0.0  # abn time projected for arriving call

        self.cell_type = CT.TEMP  # cell_types
        self.cell_mod = 0  # 1 based
        self.state = CS.NEW  # from enum
        self.completed = 0

        self.agent = 0
        self.qslot = 0

        self.t_arr = 0.0  # clock time -call arrived
        self.t_abn = 0.0  # clock time -call abandoned
        self.t_ser = 0.0  # clock time -call answered
        self.t_dep = 0.0  # clock time -call leaves ev_agent

        self.talk_time = 0.0
        self.abn_time = 0.0
        self.wait_time = 0.0

        self.cir = None

        return

    def durations(self, clock):
        talk_time = 0.0
        abn_time = 0.0
        wait_time = 0.0
        call_state = self.state

        # IDLE=0		#'not yet in system'
        # IMM_BLOCK=1	#'Blocked'
        # ANS_IMM=2	    #'Talking immediate answer'
        # IN_Q=3		#'In queue'
        # IN_Q_T=4		#'In queue - longer than T seconds'
        # ANS_DELAY=5   #'Talking after queuing'
        # COMPLETED=9	#'Left system'

        if call_state == CS.ANS_IMM:
            talk_time = clock - self.t_arr
        elif call_state == CS.IN_Q:
            wait_time = clock - self.t_ser
        elif call_state == CS.ANS_DELAY:
            wait_time = self.t_ser - self.t_arr
            talk_time = clock - self.t_ser
        else:
            wait_time = self.t_ser - self.t_arr
            talk_time = self.t_dep - self.t_ser

        self.talk_time = talk_time
        self.abn_time = abn_time
        self.wait_time = wait_time

        return talk_time, wait_time, abn_time


def main():
    # testing 
    cust = Cust()
    print(cust.cir)

    cir = qsp.cir_init(cust, cell_rc=(1, 1))
    print(cir)

    qsp.cir_move(cir, cir_xy=(8, 16))
    print(cir)

    cust.state = CS.ANS_DELAY
    cust.t_arr = 10
    cust.t_ser = 70
    cust.t_dep = 0

    Cust.durations(cust, 100)
    display(cust)

    cust2 = Cust()
    print(cust2.cir)

    cir2 = qsp.cir_init(cust2, cell_rc=(1, 1))
    print(cir2)

    qsp.cir_move(cir2, cir_xy=(20, 20))
    print(cir2)

    cust2.state = CS.ANS_IMM
    cust2.t_arr = 30
    cust2.t_ser = 70
    cust2.t_dep = 100

    Cust.durations(cust2, 100)
    display(cust)

    return


if __name__ == "__main__":
    main()

pass
