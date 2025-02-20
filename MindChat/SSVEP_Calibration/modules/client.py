import gc
# gc.disable()
# import psutil
# p = psutil.Process()
# p.nice(psutil.REALTIME_PRIORITY_CLASS)
from SSVEP_Calibration.cfg import *
import os
os.chdir(WORK_DIR)
import ctypes
import time
import numpy as np
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QMutex, Qt, QTimer, QCoreApplication
from PyQt6.QtGui import QKeyEvent, QSurfaceFormat, QFont, QGuiApplication
from SSVEP_Calibration.modules.SSVEP import Player, Stimulator
import sys
from functools import partial


class Client(QOpenGLWidget):
    def __init__(self):
        super(Client, self).__init__()
        geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, geometry.width(), geometry.height())

        self.player = Player(self, geometry.width(), geometry.height())

        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)
        self.vlayout.addWidget(self.player)

        self.stimulator = Stimulator(self)
        self.stimuliTimer = QTimer(self)

        self.initMetaData()
        self.initSignalSlot()
        self.stimulator.start()

    def initMetaData(self):
        self.wt = time.time()
        self.stimuliTimer.setTimerType(Qt.TimerType.PreciseTimer)
        self.isRunning = True
        self.pause()

    def initSignalSlot(self):
        self.stimulator.stimulation.connect(self.process)

    def process(self, stimulation: dict):
        state = stimulation['state']
        self.player.state = state
        if state == mState.STATE_NULL:
            if self.isRunning:
                self.pause()
            self.player.process(**stimulation)
        elif state == mState.STATE_STIMULI:
            stimulation['warm up'] = True
            self.wt = time.time()
            self.stimuliTimer.timeout.connect(partial(self.on_stimuliTimer_timeout, stimulation))
            self.stimuliTimer.start(mStateDur.STATE_STIMULI_STEP)
        elif state == mState.STATE_RELAX:
            if self.stimuliTimer.isActive():
                self.stimuliTimer.stop()
                self.stimuliTimer.disconnect()
            self.player.process(**stimulation)
        elif state == mState.STATE_TABLE:
            gc.collect()
            self.player.process(**stimulation)
        else:
            self.player.process(**stimulation)

    def on_stimuliTimer_timeout(self, stimulation):
        if stimulation['state'] != self.player.state:
            return

        if stimulation['warm up']:
            if time.time() - self.wt > 0.1:
                stimulation['warm up'] = False

        s = time.time()
        self.player.process(**stimulation)
        e = time.time()
        if e - s > 0.002 and e - self.wt < mStateDur.STATE_STIMULI_DUR and not stimulation['warm up']:
            print(f'dif {e-s}')
            print(f'time {e - self.wt}')

    def pause(self):
        # be cautious to use this function
        print(f'experiment pause')
        if self.isRunning:
            self.isRunning = False
            self.stimulator.mutex.lock()
            self.stimulator.event.set()
        if self.stimuliTimer.isActive():
            self.stimuliTimer.stop()
            self.stimuliTimer.disconnect()

    def keyReleaseEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Space:
            if self.isRunning:
                self.pause()
            else:
                print(f'experiment resume')
                self.isRunning = not self.isRunning
                self.stimulator.mutex.unlock()
        elif a0.key() == Qt.Key.Key_Escape:
            self.close()
        a0.accept()

    def closeEvent(self, a0) -> None:
        self.stimulator.terminate()
        a0.accept()


if __name__ == '__main__':
    scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Floor)

    format = QSurfaceFormat()
    format.setSwapInterval(0)
    format.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
    QSurfaceFormat.setDefaultFormat(format)

    app = QApplication([])

    client = Client()
    #client.showFullScreen()
    client.show()
    sys.exit(app.exec())