import time
import numpy as np
from PyQt6.QtCore import QThread, QMutex, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QFont, QFontMetrics
import pyqtgraph as pg
from SSVEP_Feedback.cfg import *
import math
import random
import threading
import winsound
from utils.parallelPort import ParallelPort
from typing import Union
from utils.chatbot_widget import Ui_chatbot_widget
from utils.user_widget import Ui_user_widget


class Player(pg.GraphicsView):
    def __init__(self, parent=None, width=1920, height=1080):
        pg.setConfigOptions(background=(127, 127, 127))
        pg.setConfigOptions(useOpenGL=True)
        super(Player, self).__init__(parent)

        self.view = pg.ViewBox()
        self.setCentralWidget(self.view)

        self.view.enableAutoRange(x=False, y=False)
        self.view.setMouseEnabled(False, False)
        self.view.setMenuEnabled(False)
        self.xRange = [-(width // 2), width // 2-1]
        self.yRange = [-(height // 2), height // 2-1]
        self.view.setXRange(*self.xRange, padding=0)
        self.view.setYRange(*self.yRange, padding=0)

        self.trigger = ParallelPort(TRIGGER_PORT)
        self.triggerStopTimer = QTimer(self)
        self.triggerStopTimer.timeout.connect(self.on_triggerStopTimer_timeout)
        self.triggerStopTimer.setSingleShot(True)
        self.triggerStopTimer.start(int(1/FS*1000*2)+1)

        self.initMetaData()

    def initMetaData(self):
        self.state = None
        self.pre_state = None
        self.rows, self.columns = ROWS, COLUMNS
        assert self.rows * self.columns == len(TARGET)
        self.rstep, self.cstep = 1, 1
        self.esize = (110, 110)

        self.imageLevels = (-1, 1) # colormap range
        self.imageShape = ((self.rows-1)*(self.rstep+1)+1, (self.columns-1)*(self.cstep+1)+1)
        self.imageH, self.imageW = self.imageShape[0]*self.esize[0], self.imageShape[1]*self.esize[1]
        self.imageRect = (-self.imageW/2, -self.imageH/2, self.imageW, self.imageH)
        self.imageItem = self.draw_image(np.zeros(self.imageShape, dtype=np.float64), rect=self.imageRect, levels=self.imageLevels)
        self.initialT = None

        self.dfcol = (255, 255, 255)
        self.tableItems = []
        px, py = (-self.imageW/2+self.esize[0]/2, self.imageH/2-self.esize[1]/2)
        for r in range(self.rows):
            y = py - r*(self.rstep+1)*self.esize[0]
            for c in range(self.columns):
                x = px + c*(self.cstep+1)*self.esize[1]
                tableItem = self.draw_text(TYPE_TEXT_TABLE[TARGET[r*self.columns+c]], x, y, size=int((self.esize[0]+self.esize[1])/2*0.5))
                self.tableItems.append(tableItem)

    def process(self, state: mState = mState.STATE_NULL, **kwargs):
        self.view.clear()

        if state == mState.STATE_TABLE:
            self.initialT = None
            t = threading.Thread(target=lambda :winsound.Beep(500, 500))
            t.start()
            for tableItem in self.tableItems:
                self.view.addItem(tableItem)
        elif state == mState.STATE_STIMULI:
            #todo need to modify the ImageItem class
            if kwargs['warm up']:
                imageItem = self.draw_image(np.zeros(self.imageShape), self.imageRect, self.imageLevels, self.imageItem)
            else:
                if self.initialT is None:
                    self.initialT = time.time()
                    self.trigger.setData(mState.STATE_STIMULI)
                    self.triggerStopTimer.start(int(1 / FS * 1000 * 2)+1)

                image = self.sinsoidal_samples(time.time())
                imageItem = self.draw_image(image, self.imageRect, self.imageLevels, self.imageItem)
            self.view.addItem(imageItem)
        elif state == mState.STATE_RESULT:
            for tableItem in self.tableItems:
                self.view.addItem(tableItem)
        elif state == mState.STATE_NULL:
            pass

        QApplication.processEvents()
        if state != self.pre_state:
            if state == mState.STATE_STIMULI:
                # todo trigger events
                pass
            self.pre_state = state

    def on_triggerStopTimer_timeout(self):
        self.trigger.setData(0)

    def sinsoidal_samples(self, curT):
        dt = curT - self.initialT
        image = []
        for i, element in enumerate(TARGET, 1):
            freq = TYPE_FREQ_TABLE[element]
            phase = TYPE_PHASE_TABLE[element]
            image.append(math.sin(2*math.pi*freq*dt+phase*math.pi))
            if i % self.columns:
                image.extend([0]*self.cstep)
            elif i != len(TARGET):
                for _ in range(self.rstep):
                    image.extend([0] * self.imageShape[1])
        image = np.array(image).reshape(*self.imageShape)
        image = np.transpose(image[::-1], [1, 0])
        return image

    def draw_image(self, array, rect, levels=(-1, 1), imageItem: pg.ImageItem = None):
        if imageItem:
            imageItem.updateImage(array, rect=rect, levels=levels)
        else:
            imageItem = pg.ImageItem(array, rect=rect, levels=levels)
        return imageItem

    def draw_text(self, text, x, y, color=(255, 255, 255), size=100):
        if len(text) == 1:
            textItem = pg.TextItem(
                html=f'<div style="text-align: center">'
                     f'<span style="font-size: {size}pt; font-wight: bold; font-family: Arial;">{text}</span></div>',
                anchor=(0.5, 0.5))
            textItem.setColor(color)
        else:
            textItem = pg.TextItem(
                html=f'<img src="{text}" width="50" height="50"/>',
                anchor=(0.5, 0.5))
        textItem.setPos(x, y)
        return textItem


def createMessageClass(cls):
    class Message(QWidget, cls):
        def __init__(self, parent=None):
            super(Message, self).__init__(parent)
            self.setupUi(self)
            self.font = self.textBrowser.font()
            self.fm = self.textBrowser.fontMetrics()
            self.maxWidth = 300
            self.widthMargin = self.textBrowser.contentsMargins().left() * 2 + 12
            self.heightMargin = self.textBrowser.contentsMargins().top() * 2 + 30 + 8

        def setText(self, text: str):
            self.textBrowser.setText(text)
            text_width = 0
            text_height = 0
            for s in (ss := text.split('\n')):
                w = self.fm.boundingRect(s).width()
                h = self.fm.boundingRect(text).height()

                if w + self.widthMargin > self.maxWidth:
                    h = math.ceil(w / (self.maxWidth - self.widthMargin)) * h
                    w = self.maxWidth - self.widthMargin
                text_width = max(text_width, w)
                text_height += h
            text_height += max(text.count('\n') - len(ss), 0) * self.fm.boundingRect(text).height()

            self.textBrowser.setMinimumWidth(text_width + self.widthMargin)
            self.textBrowser.setMaximumWidth(text_width + self.widthMargin)
            self.setMinimumHeight(text_height + self.heightMargin)
            self.setMaximumHeight(text_height + self.heightMargin)
    return Message


class Stimulator(QThread):
    stimulation = pyqtSignal(dict)

    def __init__(self, parent = None):
        super(Stimulator, self).__init__(parent)
        self.mutex = QMutex()
        self.event = threading.Event()
        self.endRunFlag = False
        self.trialTimeoutFlag = False

    def run(self):
        self.waiting(1)

        for run in range(RUN_NUM):
            print('start a new run!')
            self.stimulation.emit({'state': mState.STATE_NULL})
            self.waiting(1)
            self.sleep(2)
            self.endRunFlag = False

            for idx in range(MAX_TRIAL_NUM):
                print(f'run {run}, trial {idx+1}')
                self.trialTimeoutFlag = False

                self.stimulation.emit({'state':mState.STATE_TABLE, 'trial': idx})
                self.waiting(mStateDur.STATE_TABLE_DUR + (1.5 if not idx else 0))

                self.stimulation.emit({'state':mState.STATE_STIMULI})
                self.waiting(mStateDur.STATE_STIMULI_DUR)

                self.stimulation.emit({'state':mState.STATE_RESULT})
                self.waiting(1) # for computation time cost, can be any > 0
                if not self.trialTimeoutFlag:
                    self.waiting(mStateDur.STATE_RESULT_DUR)
                if self.endRunFlag:
                    break
            else:
                self.endRunFlag = True
                self.stimulation.emit({'state':mState.STATE_RESULT})
                self.waiting(1)  # for computation time cost, can be any > 0
                if not self.trialTimeoutFlag:
                    self.waiting(mStateDur.STATE_RESULT_DUR)
            if not self.trialTimeoutFlag:
                self.sleep(1)
        print('End of the experiment!')

    def waiting(self, duration):
        self.event.clear()
        self.event.wait(duration)
        self.mutex.lock()
        self.mutex.unlock()