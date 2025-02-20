from enum import Enum
import random


class SSVEPType:
    TYPE_01  = 1
    TYPE_02  = 2
    TYPE_03  = 3
    TYPE_04  = 4
    TYPE_05  = 5
    TYPE_06  = 6
    TYPE_07  = 7
    TYPE_08  = 8
    TYPE_09  = 9
    TYPE_10  = 10
    TYPE_11  = 11
    TYPE_12  = 12
    TYPE_13  = 13
    TYPE_14  = 14
    TYPE_15  = 15
    TYPE_16  = 16
    TYPE_17  = 17
    TYPE_18  = 18
    TYPE_19  = 19
    TYPE_20  = 20
    TYPE_21  = 21
    TYPE_22  = 22
    TYPE_23  = 23
    TYPE_24  = 24
    TYPE_25  = 25
    TYPE_26  = 26
    TYPE_27  = 27
    TYPE_28  = 28
    TYPE_29  = 29
    TYPE_30  = 30
    TYPE_31  = 31
    TYPE_32  = 32
    TYPE_33  = 33
    TYPE_34  = 34
    TYPE_35  = 35
    TYPE_36  = 36
    TYPE_37  = 37
    TYPE_38  = 38
    TYPE_39  = 39
    TYPE_40  = 40

TYPE_TEXT_TABLE = {
    1: 'a',
    2: 'b',
    3: 'c',
    4: 'd',
    5: 'e',
    6: 'f',
    7: 'g',
    8: 'h',
    9: 'i',
    10: 'j',
    11: 'k',
    12: 'l',
    13: 'm',
    14: 'n',
    15: 'o',
    16: 'p',
    17: 'q',
    18: 'r',
    19: 's',
    20: 't',
    21: 'u',
    22: 'v',
    23: 'w',
    24: 'x',
    25: 'y',
    26: 'z',
    27: 'utils/icons/comma.png',
    28: 'utils/icons/query.png',
    29: 'utils/icons/apostrophe.png',
    30: 'utils/icons/space.png',
    31: 'utils/icons/undo.png',
    32: 'utils/icons/del.png',
    33: '0',
    34: '1',
    35: '2',
    36: '3',
    37: '4',
    38: '5',
    39: '6',
    40: 'utils/icons/enter.png',
}

TYPE_FREQ_TABLE = {
    1: 8,
    2: 9,
    3: 10,
    4: 11,
    5: 12,
    6: 13,
    7: 14,
    8: 15,
    9: 8.2,
    10: 9.2,
    11: 10.2,
    12: 11.2,
    13: 12.2,
    14: 13.2,
    15: 14.2,
    16: 15.2,
    17: 8.4,
    18: 9.4,
    19: 10.4,
    20: 11.4,
    21: 12.4,
    22: 13.4,
    23: 14.4,
    24: 15.4,
    25: 8.6,
    26: 9.6,
    27: 10.6,
    28: 11.6,
    29: 12.6,
    30: 13.6,
    31: 14.6,
    32: 15.6,
    33: 8.8,
    34: 9.8,
    35: 10.8,
    36: 11.8,
    37: 12.8,
    38: 13.8,
    39: 14.8,
    40: 15.8,
}
TYPE_PHASE_TABLE = {
    1: 0,
    2: 0.5,
    3: 1,
    4: 1.5,
    5: 0,
    6: 0.5,
    7: 1,
    8: 1.5,
    9: 0,
    10: 0.5,
    11: 1,
    12: 1.5,
    13: 0,
    14: 0.5,
    15: 1,
    16: 1.5,
    17: 0,
    18: 0.5,
    19: 1,
    20: 1.5,
    21: 0,
    22: 0.5,
    23: 1,
    24: 1.5,
    25: 0,
    26: 0.5,
    27: 1,
    28: 1.5,
    29: 0,
    30: 0.5,
    31: 1,
    32: 1.5,
    33: 0,
    34: 0.5,
    35: 1,
    36: 1.5,
    37: 0,
    38: 0.5,
    39: 1,
    40: 1.5,
}

TARGET = [TYPE for TYPE in TYPE_TEXT_TABLE] # should be in order
DECODE_TYPE = TARGET
ROWS, COLUMNS = 5, 8

class mState:
    STATE_NULL          = -1
    STATE_PAUSE         = -2
    STATE_TABLE         = 100
    STATE_STIMULI       = 101
    STATE_RESULT        = 102

class mStateDur:
    STATE_TABLE_DUR     = 1 # 1
    STATE_STIMULI_DUR   = 1.65 # including 0.1warm up + 0.05transition
    STATE_STIMULI_STEP  = 2 #msec
    STATE_RESULT_DUR    = 3 # 1.5

class mModel:
    FBECCA   = 1000
    FBTRCA   = 1001
    FBTDCA   = 1002

DATASET_FILE = r'~\MindChat\data\multi-turn daily dialogue.xlsx'
RUN_NUM = 4
MAX_TRIAL_NUM = 500
MAX_MESSAGE_DELAY = 10000 # ssvep + chatgpt

IPADDRESS_DECODER = '127.0.0.1'
IP_PORT_DECODER = 23618
IPADDRESS_CHATBOT = '127.0.0.1'
IP_PORT_CHATBOT = 24618
TRIGGER_PORT = '0x3FF8'

TIME_LENGTH = 6
PULL_INTERVAL = 0.01
FS = 1200
RESAMPLE = 5    # for decoding
DATA_DUR = (0, 1.5)
WIN_DUR = (0.2, 1.5)

REF_CHANS = [9, 10]
MARKER_CHAN = [11]
CHANS = [
         1, 2, 3, 4, 5, 6, 7, 8, 9,
         # 47, 48, 49,
         # 54, 55, 56,
         # 58, 59, 60,
         ]
CHANS = [c-1 for c in CHANS]
BAD_CHANS = []

WORK_DIR = '~/MindChat/'
CHANS_NAMES = ["FP1","FPZ","FP2","AF7","AF3","AF4","AF8","F7","F5","F3","F1","FZ","F2","F4","F6",
    "F8","FT7","FC5","FC3","FC1","FCz","FC2","FC4","FC6","FT8","T7","C5","C3","C1","Cz","C2","C4",
    "C6","T8","TP7","CP5","CP3","CP1","CPZ","CP2","CP4","CP6","TP8","P7","P5","P3","P1","PZ","P2",
    "P4","P6","P8","PO7","PO3","POz","PO4","PO8","O1","Oz","O2","F9","F10"]
CHANS_LOC_FILE = f'{WORK_DIR}/utils/getec62.sfp'

SUBJECT_NAME = 'XXX'

MODEL_PATH = {
    mModel.FBECCA: f'{WORK_DIR}/SSVEP_Feedback/resources/{SUBJECT_NAME}/{SUBJECT_NAME}_FBECCA_s1_40class_1s.pkl',
    #mModel.FBTRCA: f'{WORK_DIR}/SSVEP_Feedback/resources/{SUBJECT_NAME}/{SUBJECT_NAME}_FBTRCA_s1_16class_2s.pkl',
}
MODEL_SET = [model for model in MODEL_PATH]
MODEL_QUEUE = []
for i in range(RUN_NUM // len(MODEL_SET)):
    #random.shuffle(MODEL_SET)
    MODEL_QUEUE += MODEL_SET

CHAT_INPUT_MODE = 1