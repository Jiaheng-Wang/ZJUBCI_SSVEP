import time
from .FBECCA import FBECCA
from numpy import ndarray
from .base import generate_filterbank
from scipy.signal import sosfiltfilt, iirnotch, filtfilt
import numpy as np
import resampy


class OnlineFBECCA:
    def __init__(self, config: dict, model: FBECCA):
        self.config = config
        self.model = model
        self.filterbank = generate_filterbank([[self.config['freqs'][0], 48]], [[self.config['freqs'][0] - 2, 50]], self.config['fs']//self.config['resample'],
                                         order=4, rp=1)

    def __call__(self, data: ndarray):
        data = data[None, ...]
        fs = self.config['fs']
        if self.config['data_dur']:
            e = int((self.config['data_dur'][1] - self.config['data_dur'][0]) * fs)
            data = data[..., :e]
        N, C, T = data.shape
        data = resampy.resample(data, fs, fs // self.config['resample'])

        fs = fs // self.config['resample']

        b, a = iirnotch(50, 25, fs)
        data = filtfilt(b, a, data, axis=-1)
        # data = sosfiltfilt(self.filterbank[0], data, axis=-1)

        if self.config['win_dur']:
            s = int((self.config['win_dur'][0] - self.config['data_dur'][0]) * fs)
            e = int((self.config['win_dur'][1] - self.config['data_dur'][0]) * fs)
            data = data[..., s:e]
        data = data - np.mean(data, axis=-1, keepdims=True)

        pred = self.model.predict(data)
        return pred