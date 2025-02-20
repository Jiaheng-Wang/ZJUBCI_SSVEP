import time
import numpy as np
import math
import pylsl
from PyQt6.QtCore import QThread, pyqtSignal, QMutex
from SSVEP_Feedback.cfg import *
from .tools import make_interpolation_matrix


class Inlet:
    """Base class to represent an inlet"""
    dtypes = [None, np.float32, np.float64, str, np.int32, np.int16, np.int8, np.int64]
    def __init__(self, info: pylsl.StreamInfo):
        # create an inlet and connect it to the outlet we found earlier.
        # max_buflen is set so data older the plot_duration is discarded
        # automatically and we only pull data new enough to show it

        # Also, perform online clock synchronization so all streams are in the
        # same time domain as the local lsl_clock()
        # (see https://labstreaminglayer.readthedocs.io/projects/liblsl/ref/enums.html#_CPPv414proc_clocksync)
        # and dejitter timestamps
        self.time_length = TIME_LENGTH
        self.inlet = pylsl.StreamInlet(info, max_buflen = self.time_length,
                                       processing_flags = pylsl.proc_clocksync) #pylsl.proc_dejitter
        self.info = info
        self.name = info.name()
        self.type = info.type()
        self.channel_count = info.channel_count()
        self.fs = info.nominal_srate()

        self.data = np.zeros((self.channel_count, 1), dtype = self.dtypes[info.channel_format()])
        self.ts = np.zeros(1, dtype = np.float32) - 100 #初始时间

    def update(self, y, ts, store_time):
        old_offset = self.ts.searchsorted(store_time)
        #new_offset = ts.searchsorted(max(store_time, self.ts[-1]), side='right')
        new_offset = ts.searchsorted(store_time, side='right')  # keep all feasible data

        self.ts = np.hstack((self.ts[old_offset:], ts[new_offset:]))
        self.data = np.hstack((self.data[:, old_offset:], y[:, new_offset:]))


class CompositeInlet(Inlet, QThread):
    def __init__(self, info: pylsl.StreamInfo):
        Inlet.__init__(self, info)
        QThread.__init__(self)

        self.channel_count = info.channel_count() - len(REF_CHANS) if not CHANS else len(CHANS) + len(MARKER_CHAN)
        assert min(REF_CHANS, default=float('inf')) > max(CHANS)
        assert min(MARKER_CHAN) > max(REF_CHANS, default=float('-inf'))
        self.data = np.zeros((self.channel_count, 1), dtype = self.dtypes[info.channel_format()])
        self.markers = self.data[-1]

        # inplace operation, more efficient
        bufferSize = (math.ceil(self.fs * self.time_length), info.channel_count())
        self.buffer = np.empty(bufferSize, dtype = self.dtypes[info.channel_format()])
        self.dtype = self.dtypes[info.channel_format()]
        self.pull_interval = PULL_INTERVAL
        self.is_running = False

        if BAD_CHANS:
            self.interpolation_matrix = make_interpolation_matrix(CHANS_NAMES, CHANS_LOC_FILE, self.fs, BAD_CHANS)
        self.mutex = QMutex()

    def run(self):
        self.is_running = True
        self.inlet.open_stream(timeout=1)
        self.start_time = pylsl.local_clock()

        self.data = np.zeros((self.channel_count, 1), dtype = self.dtypes[self.info.channel_format()])
        self.markers = self.data[-1]
        self.ts = np.zeros(1, dtype = np.float32) - 100
        print(f'CompositeInlet subThread has been opened.')

        while self.is_running:
            curr_time = pylsl.local_clock() - self.start_time
            next_time = curr_time + self.pull_interval + self.start_time
            store_time = curr_time - self.time_length

            _, ts = self.inlet.pull_chunk(timeout=0.001,
                                          max_samples=self.buffer.shape[0],
                                          dest_obj=self.buffer)
            if ts:
                self.mutex.lock()

                y = self.buffer[:len(ts), :].transpose((1, 0))
                ts = np.asarray(ts, dtype=np.float32) - self.start_time

                markers = y[MARKER_CHAN]
                if REF_CHANS:
                    y_ref = y[REF_CHANS, :]
                    y_ref = np.mean(y_ref, axis=0, keepdims=True)
                    np.subtract(y, y_ref, out=y)
                if BAD_CHANS:
                    y[BAD_CHANS] = np.matmul(self.interpolation_matrix, np.delete(y[:len(CHANS_NAMES)], BAD_CHANS, axis=0))
                y = y[CHANS+MARKER_CHAN]
                y[-1] = markers

                self.update(y, ts, store_time)
                self.markers = self.data[-1]
                self.mutex.unlock()

            sleep = max(0, next_time - pylsl.local_clock())
            self.msleep(round(sleep * 1000))

    def get_data_by_marker(self, marker: int, startT: float, endT: float):
        self.mutex.lock()
        markers = np.diff(self.markers)
        markers = np.maximum(markers, 0)

        # markers[-2400] = marker

        idx = np.argwhere(markers == marker)[-1][0] + 1
        s, e = int(idx + self.fs * startT), int(idx + self.fs * endT)
        data = self.data[:-1, s:e] # might cause one sample bias
        self.mutex.unlock()
        return data

    def stop(self):
        self.is_running = False
        self.wait()
        self.inlet.close_stream()
        print("CompositeInlet subThread has been closed.")