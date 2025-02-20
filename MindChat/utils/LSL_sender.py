import time
from pylsl import StreamInfo, StreamOutlet
import pylsl
import numpy as np


cn = 11
fs = 1200
interval = 40 #ms
info = StreamInfo('g.tec', 'EEG', cn, fs, pylsl.cf_float32, 'BCILab')
outlet = StreamOutlet(info)

print("now sending data...")

while True:
    # mysample = np.random.randn(cn).astype(np.float32)*25
    # outlet.push_sample(mysample)
    # time.sleep(1/fs)

    mysamples = np.random.randn(int(fs/interval), cn).astype(np.float32)*25
    outlet.push_chunk(mysamples)
    time.sleep(interval/1000)
