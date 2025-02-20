import numpy as np
import pickle
from SSVEP_Feedback.cfg import *
import random
import time
import warnings

import sys, os
root = os.getcwd() + '/algorithms/'
[sys.path.append(root + dir) for dir in os.listdir(root)]


class Decoder():
    def __init__(self):
        self.fs = FS
        self.win_dur = WIN_DUR

    def setModel(self, path):
        self.model_path = path
        print(f'Using {path.split("/")[-1]} as decoders')

        if 'FBECCA' in self.model_path:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)[0]
        elif 'FBTRCA~' in self.model_path:
            pass
        else:
            self.model = None
            warnings.warn('random decoder!')

    def process(self, data):

        if 'FBECCA' in self.model_path:
            pred_label = self.model(data).item()
            #pred_label = min((pred_label, 15))
        else:
            '''Random Decoder'''
            pred = [random.random() for _ in range(len(DECODE_TYPE))]
            pred_label = max(range(len(pred)), key=lambda i:pred[i])

        pred = DECODE_TYPE[pred_label]
        return pred