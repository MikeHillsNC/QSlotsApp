"""set qslot tables"""
import pandas as pd
import IPython
from IPython.display import display


# ---------------------------------
def import_dataframes(s, debug=0):
    # ---------------------------------
    # ---------------------------------
    # def build_dfQS_pathsQ(self,debug=0):
    s.dfq = pd.read_excel("qslots.xlsx",sheet_name="dfQS_pathsQ", index_col=0, header=0, usecols="A:F", nrows=93)
    s.dfq = s.dfq[s.dfq.index % 2 == 0]  # select even rows
    if debug > 0:
        s.dfq.info()
        display(s.dfq)

    # def build_dfQS_system():
    s.dfs = pd.read_excel("QSlots.xlsx", sheet_name="dfQS_system3", index_col=0, header=0, usecols="A:S", nrows=43, )

    if debug > 0:
        s.dfs.info()
        display(s.dfs)
    """
        na_valuesscalar: str, list-like, or dict, default None
            By default the following values are interpreted as NaN: ‘’, ... ‘null’.

        keep_default_nabool:default True
            Whether or not to include the default NaN values when parsing the data.
            Depending on whether na_values is passed in, the behavior is as follows:
                If keep_default_na is True
                        and na_values are specified, na_values is appended to the default NaN values used for parsing.
                        and na_values are not specified, only the default NaN values are used for parsing.  XXXXXX
                
                If keep_default_na is False
                        and na_values are specified, only the NaN values specified na_values are used for parsing.
                        and na_values are not specified, no strings will be parsed as NaN.

            Note that if na_filter is passed in as False, the keep_default_na and na_values parameters will be ignored.
            
        na_filterbool:default True
            Detect missing value markers (empty strings and the value of na_values).
            In data without any NAs, passing na_filter=False can improve the performance of reading a large file.
    """

    # ---------------------------------
    # def build_dfQS_map():
    s.dfm = pd.read_excel("qslots.xlsx",
                          sheet_name="dfQS_map", index_col=0, header=0, usecols="A:P",
                          dtype={'label': str, 'labelNext': str, 'labelAlt': str})

    if debug > 0:
        s.dfm.info()
        display(s.dfm)
    # ---------------------------------
    # def build_dfQS_frame():
    s.dff = pd.read_excel("qslots.xlsx",
                          sheet_name="dfQS_frame", index_col=0, header=0, usecols="A:G", nrows=24)
    if debug > 0:
        s.dff.info()
        display(s.dff)
    # ---------------------------------
    # def build_dfQS_paths():
    s.dfp = pd.read_excel("qslots.xlsx",
                          sheet_name="dfQS_paths3", index_col=0, header=0, usecols="A:AN", nrows=16)
    if debug > 0:
        s.dfp.info()
        display(s.dfp)

    # ---------------------------------
    # def build_dfQS_calls():
    s.dfc = pd.read_excel("qslots.xlsx",
                          sheet_name="dfQS_calls", index_col=0, header=0, usecols="A:O", nrows=1)
    if debug > 0:
        s.dfc.info()
        display(s.dfc)

    s.dfcomb = s.dfs.merge(s.dfp, how='left', on='iD_cell')

    return

    # ---------------------------

    # if __name__ == "__main__":
    #     main()
    #
    # pass

    """
    ----------------
    system
    ----------------
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 43 entries, 0 to 42
    Data columns (total 18 columns):
    #   Column           Non-Null Count  Dtype
    ---  ------           --------------  -----
    0   iD_cell          43 non-null     int64
    1   label            43 non-null     object
    2   labelNext        35 non-null     object
    3   cell_type        43 non-null     object
    4   cell_mod         43 non-null     int64
    5   status           21 non-null     object
    6   id_call          43 non-null     int64
    7   cust         0 non-null      float64
    8   final_state      0 non-null      float64
    9   current_row      43 non-null     int64
    10  current_col      43 non-null     int64
    11  current_x        43 non-null     int64
    12  current_y        43 non-null     int64
    13  t_arrival        43 non-null     int64
    14  t_serviced       43 non-null     int64
    15  t_departure      43 non-null     int64
    16  time_in_Q        43 non-null     int64
    17  time_in_service  43 non-null     int64
    dtypes: float64(2), int64(12), object(4)
    memory usage: 6.4+ KB

        iD_cell          label   labelNext cell_type  cell_mod  ... t_arrival  t_serviced  t_departure  time_in_Q  time_in_service
    iD                                                          ...
    0        81       NewCall0    NewCall1         T         0  ...         0           0            0          0                0
    1        71       NewCall1     QSlot01         T         0  ...         0           0            0          0                0
    2        41        QSlot00  NextAgent1         T         0  ...         0           0            0          0                0
    3        43        QSlot01     QSlot00         Q         1  ...         0           0            0          0                0
    ...
    17       74        QSlot15     QSlot14         Q        15  ...         0           0            0          0                0
    18       73        QSlot16     QSlot15         Q        16  ...         0           0            0          0                0
    19       31     NextAgent1      Agent1         N         1  ...         0           0            0          0                0
    ...
    26       38     NextAgent8      Agent8         N         8  ...         0           0            0          0                0
    27       21         Agent1  Departures         A         1  ...         0           0            0          0                0
    ...
    34       28         Agent8  Departures         A         8  ...         0           0            0          0                0
    35       89  CallsReceived         NaN         T         0  ...         0           0            0          0                0
    36       79        Blocked         NaN         T         0  ...         0           0            0          0                0
    37       69         ImmAns         NaN         T         0  ...         0           0            0          0                0
    38       59        ImmAban         NaN         T         0  ...         0           0            0          0                0
    39       49         Queued         NaN         T         0  ...         0           0            0          0                0
    40       39    DelayedAban         NaN         T         0  ...         0           0            0          0                0
    41       29     Departures         NaN         T         0  ...         0           0            0          0                0
    42       19          Total         NaN         T         0  ...         0           0            0          0                0

    [43 rows x 18 columns]
    """

    """
    -------
    map
    -------
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 81 entries, 11 to 99
    Data columns (total 15 columns):
    #   Column     Non-Null Count  Dtype
    ---  ------     --------------  -----
    0   iD_Agent   81 non-null     int64
    1   iD_QSlot   81 non-null     int64
    2   row        81 non-null     int64
    3   col        81 non-null     int64
    4   center_x   81 non-null     int64
    5   center_y   81 non-null     int64
    6   iNext      81 non-null     int64
    7   jNext      81 non-null     int64
    8   iAlt       81 non-null     int64
    9   jAlt       81 non-null     int64
    10  pathCode   16 non-null     object
    11  label      29 non-null     object
    12  labelNext  25 non-null     object
    13  labelAlt   0 non-null      object
    14  cust   0 non-null      float64
    dtypes: float64(1), int64(10), object(4)
    memory usage: 10.1+ KB

            iD_Agent  iD_QSlot  row  col  center_x  center_y  iNext  jNext  iAlt  jAlt pathCode         label labelNext labelAlt  cust
    iD_cell
    11              0         0    1    1         8         8      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    12              0         0    1    2        24         8      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    13              0         0    1    3        40         8      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    14              0         0    1    4        56         8      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    15              0         0    1    5        72         8      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    ...           ...       ...  ...  ...       ...       ...    ...    ...   ...   ...      ...           ...       ...      ...       ...
    95              0         0    9    5        72       136      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    96              0         0    9    6        88       136      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    97              0         0    9    7       104       136      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    98              0         0    9    8       120       136      0      0     0     0      NaN           NaN       NaN      NaN       NaN
    99              0         0    9    9       136       136      0      0     0     0      NaN  callResevoir       NaN      NaN       NaN

    [81 rows x 15 columns]

    """

    """
    -------------
    frame
    -------------
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 7 entries, 1 to 7
    Data columns (total 4 columns):
    #   Column  Non-Null Count  Dtype
    ---  ------  --------------  -----
    0   i1      7 non-null      int64
    1   j1      7 non-null      int64
    2   i2      7 non-null      int64
    3   j2      7 non-null      int64
    dtypes: int64(4)
    memory usage: 280.0 bytes

        i1   j1   i2   j2 TYPE  MOD
    iD
    1   112   16  112  112    Q    0
    2   112  112   48  112    Q    0
    3    48  112   48   16    Q    0
    4    64   16   96   16    Q    0
    5    96   16   96   88    Q    0
    6    80   40   80  112    Q    0
    7    64   16   64   88    Q    0
    8    16    0   32    0    A    0
    9    16    0   16   16    A    1
    10   16   16   32   16    A    1
    11   16   16   16   32    A    2
    12   16   16   32   32    A    2
    13   16   32   16   48    A    3
    14   16   32   32   48    A    3
    15   16   48   16   64    A    4
    16   16   48   32   64    A    4
    17   16   64   16   80    A    5
    18   16   64   32   80    A    5
    19   16   80   16   96    A    6
    20   16   80   32   96    A    6
    21   16   96   16  112    A    7
    22   16   96   32  112    A    7
    23   16  112   16  128    A    8
    24   16  112   32  128    A    8
    """

    """
    ---------------
    paths
    ---------------
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 16 entries, 43 to 73
    Data columns (total 38 columns):
    #   Column  Non-Null Count  Dtype
    ---  ------  --------------  -----
    0   next_x  16 non-null     int64
    1   next_y  16 non-null     int64
    2   new_x   16 non-null     int64
    3   new_y   16 non-null     int64
    4   x0      16 non-null     int64
    5   x1      16 non-null     float64
    6   x2      16 non-null     float64
    ..
    19  x15     16 non-null     float64
    20  x16     16 non-null     int64
    21  y0      16 non-null     int64
    22  y1      16 non-null     float64
    ...
    36  y15     16 non-null     float64
    37  y16     16 non-null     int64
    dtypes: float64(29), int64(9)
    memory usage: 4.9 KB

            next_x  next_y  new_x  new_y  x0        x1      x2  ...        y10         y11        y12         y13      y14         y15  y16
    iD_cell                                                      ...
    43            8      56      0      0  40  38.00000  36.000  ...   56.00000   56.000000   56.00000   56.000000   56.000   56.000000   56      
    44           40      56      0      0  56  55.00000  54.000  ...   56.00000   56.000000   56.00000   56.000000   56.000   56.000000   56      
    45           56      56      0      0  72  71.00000  70.000  ...   56.00000   56.000000   56.00000   56.000000   56.000   56.000000   56      
    46           72      56      0      0  88  87.00000  86.000  ...   56.00000   56.000000   56.00000   56.000000   56.000   56.000000   56 
    ...    
    76           88      88      0      0  88  88.99952  89.992  ...   92.67452   91.250088   90.06704   89.150904   88.506   88.125432   88      
    75           88     104      0      0  72  73.00000  74.000  ...  104.00000  104.000000  104.00000  104.000000  104.000  104.000000  104      
    74           72     104      0      0  56  57.00000  58.000  ...  104.00000  104.000000  104.00000  104.000000  104.000  104.000000  104      
    73           56     104      0      0  40  41.00000  42.000  ...  104.00000  104.000000  104.00000  104.000000  104.000  104.000000  104      

    [16 rows x 38 columns]
    """
    """
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 96 entries, 0 to 95
    Data columns (total 5 columns):
    #   Column    Non-Null Count  Dtype
    ---  ------    --------------  -----
    0   cell_mod  96 non-null     int64
    1   row       95 non-null     int64
    2   col       96 non-null     int64
    3   x         96 non-null     int64
    4   y         96 non-null     int64
    dtypes: int64(5)
    memory usage: 4.5 KB

            cell_mod  row  col   x    y
    iD_path
    0               0    7    1   8  104
    1               0    7    1  12  104
    2               0    7    1  16  104
    3               0    7    1  20  104
    4               0    7    2  24  104
    ...           ...  ...  ...  ..  ...
    92              1    4    3  40   56
    93              1    4    3  36   56
    94              1    4    3  32   56
    95              1    4    3  28   56

    [96 rows x 5 columns]

    """
    """
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 1 entries, 0 to 0
    Data columns (total 14 columns):
    #   Column          Non-Null Count  Dtype
    ---  ------          --------------  -----
    0   time            1 non-null      int64
    1   event_type      1 non-null      object
    2   current_row     1 non-null      int64
    3   current_col     1 non-null      int64
    4   current_x       1 non-null      int64
    5   current_y       1 non-null      int64
    6   id_call         1 non-null      int64
    7   cust        0 non-null      float64
    8   sys_arr_time    1 non-null      int64
    9   sys_dep_time    1 non-null      int64
    10  queue_arr_time  1 non-null      int64
    11  queue_dep_time  1 non-null      int64
    12  agent_arr_time  1 non-null      int64
    13  agent_dep_time  1 non-null      int64
    dtypes: float64(1), int64(12), object(1)
    memory usage: 120.0+ bytes

            time event_type  current_row  current_col  current_x  current_y  ...  sys_arr_time  sys_dep_time  queue_arr_time  queue_dep_time  agent_arr_time  agent_dep_time
    iD_Event                                                                   ...
    0            0      dummy            8            9        120        136  ...             0             0               0               0               0               0     

    """
