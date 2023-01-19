"""dfQS_system ROW constants for dfQS_system"""

NEWCALL0 = 0
NEWCALL1 = 1
QSLOT00 = 2
QSLOT01 = 3
QSLOT02 = 4
QSLOT03 = 5
QSLOT04 = 6
QSLOT05 = 7
QSLOT06 = 8
QSLOT07 = 9
QSLOT08 = 10
QSLOT09 = 11
QSLOT10 = 12
QSLOT11 = 13
QSLOT12 = 14
QSLOT13 = 15
QSLOT14 = 16
QSLOT15 = 17
QSLOT16 = 18
NEXTAGENT1 = 19
NEXTAGENT2 = 20
NEXTAGENT3 = 21
NEXTAGENT4 = 22
NEXTAGENT5 = 23
NEXTAGENT6 = 24
NEXTAGENT7 = 25
NEXTAGENT8 = 26
AGENT1 = 27
AGENT2 = 28
AGENT3 = 29
AGENT4 = 30
AGENT5 = 31
AGENT6 = 32
AGENT7 = 33
AGENT8 = 34
CALLSRECEIVED = 35
BLOCKED = 36
IMMANS = 37
IMMABAN = 38
QUEUED = 39
DELAYEDABAN = 40
DEPARTURES = 41
TOTAL = 42

AGENTS = [NEXTAGENT1,  # AGENTS[0] is used as waiting location for next agen
          AGENT1,
          AGENT2,
          AGENT3,
          AGENT4,
          AGENT5,
          AGENT6,
          AGENT7,
          AGENT8]

# AGENTS
# [19, 27, 28, 29, 30, 31, 32, 33, 34]

QSLOTS = [QSLOT00,
          QSLOT01,
          QSLOT02,
          QSLOT03,
          QSLOT04,
          QSLOT05,
          QSLOT06,
          QSLOT07,
          QSLOT08,
          QSLOT09,
          QSLOT10,
          QSLOT11,
          QSLOT12,
          QSLOT13,
          QSLOT14,
          QSLOT15,
          QSLOT16]

# QSLOTS
# [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, ...]

NEXTAGENTS = [QSLOT00,
              NEXTAGENT1,
              NEXTAGENT2,
              NEXTAGENT3,
              NEXTAGENT4,
              NEXTAGENT5,
              NEXTAGENT6,
              NEXTAGENT7,
              NEXTAGENT8]

# NEXTAGENTS
# [2, 19, 20, 21, 22, 23, 24, 25, 26]

# call status codes
CALL_IDLE = 'Call not yet in system'
CALL_IMMBLOCK = 'Blocked'
CALL_INQ = 'In queue'
CALL_ANS_IMM = 'Answered immediately'
CALL_ANS_DELAY = 'Answered after queuing'
CALL_COMP = 'Completed'
CALL_QTOA = 'Leave Q'

# cell status codes
CELL_INQ = CALL_INQ
CELL_INA = CALL_ANS_IMM
CELL_INA_DELAYED = CALL_ANS_DELAY
CELL_IDLE = 'Idle'

EV_ARR = 0
EV_DEP = 1
EV_ABN = 2

# event cols
EVCLOCK = 0
EVTYPE = 1
EVAGENT = 2
EVTIME = 3
EVINDEX = 4

pass
