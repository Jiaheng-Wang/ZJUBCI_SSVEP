import gc
# gc.disable()
# import psutil
# p = psutil.Process()
# p.nice(psutil.REALTIME_PRIORITY_CLASS)
import ctypes
import time
import tiktoken
import enchant
from PyQt6.QtWidgets import QWidget, QApplication,QLineEdit, QVBoxLayout
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLVersionProfile
from PyQt6.QtCore import QMutex, Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QSurfaceFormat, QFont, QGuiApplication
from PyQt6.QtNetwork import QTcpSocket, QHostAddress
from SSVEP_Feedback.cfg import *
from SSVEP_Feedback.modules.SSVEP import Player, Stimulator, createMessageClass
from SSVEP_Feedback.modules.dialogue_manager import DialogueManager, DialogueExp
from utils.tools import Depack, Pack
import sys
from functools import partial
import warnings
from utils.window import Ui_Form
from utils.chatbot_widget import Ui_chatbot_widget
from utils.user_widget import Ui_user_widget
from utils.openai_api import chat_input_completion_mode1
import os
os.chdir(WORK_DIR)


class Client(QWidget, Ui_Form):
    def __init__(self):
        super(Client, self).__init__()
        self.setupUi(self)

        geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, geometry.width(), geometry.height())

        self.tableLayout = QVBoxLayout(self.widget)
        self.tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableLayout.setSpacing(0)
        self.player = Player(self.widget, geometry.width(), (geometry.height() - 60))
        self.tableLayout.addWidget(self.player)

        self.stimulator = Stimulator(self)
        self.stimuliTimer = QTimer(self)
        self.stimuliTimer.setTimerType(Qt.TimerType.PreciseTimer)

        self.messageStreamTimer = QTimer(self)
        self.messageStreamTimer.setTimerType(Qt.TimerType.PreciseTimer)

        self.messageDelayTimer = QTimer(self)
        self.messageDelayTimer.setSingleShot(True)
        self.messageDelayTimer.setTimerType(Qt.TimerType.PreciseTimer)

        self.tcpClient_decoder = QTcpSocket(self)
        self.tcpClient_decoder.connectToHost(QHostAddress(IPADDRESS_DECODER), IP_PORT_DECODER)
        assert self.tcpClient_decoder.waitForConnected()
        print('The decoder server has been connected')

        self.tcpClient_chatbot = QTcpSocket(self)
        self.tcpClient_chatbot.connectToHost(QHostAddress(IPADDRESS_CHATBOT), IP_PORT_CHATBOT)
        assert self.tcpClient_chatbot.waitForConnected()
        print('The chatbot server has been connected')

        self.depack = Depack()
        self.pack = Pack()

        self.initMetaData()
        self.initSignalSlot()
        self.stimulator.start()

    # def initializeGL(self) -> None:
    #     return
    #     profile = QOpenGLVersionProfile()
    #     profile.setVersion(2, 0)
    #     self.gl = self.context().versionFunctions(profile)
    #     self.gl.initializeOpenGLFunctions()

    def initMetaData(self):
        self.dialogue = DialogueManager()
        self.dialogueExp = DialogueExp()
        self.dialogueExp.createTestSamples()

        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.scrollbar = self.scrollArea.verticalScrollBar()
        self.words = []
        self.utterances = []

        self.wt = time.time()
        self.isRunning = True
        self.pause()

    def initSignalSlot(self):
        self.scrollbar.rangeChanged.connect(self.on_scrollbar_rangeChanged)  # 监听窗口滚动条范围
        self.stimulator.stimulation.connect(self.process_stimulation)
        self.messageDelayTimer.timeout.connect(self.on_messageDelayTimer_timeout)
        self.tcpClient_decoder.readyRead.connect(self.readMessage)
        self.tcpClient_chatbot.readyRead.connect(self.readMessage)

    def readMessage(self):
        tcpClient = self.sender()
        if n := tcpClient.bytesAvailable():
            package = tcpClient.read(n)
            messages = self.depack.depack(package)
            for message in messages:
                if message['state'] != self.player.state:
                    #todo: can't deal with the same state in the follow-up trials
                    warnings.warn(f'delayed network transition {message}')
                    return
                self.process_message(message)

    def process_message(self, message: dict):
        if message['server'] == 'decoder':
            map = {1: 1, }
            if message['pred'] in map:
                message['pred'] = map[message['pred']]

            ptext = self.lineEdit_1.text()
            pred = message['pred']

            if pred == -1:
                self.process_invalid_message()
                return
            char = TYPE_TEXT_TABLE[message['pred']]
            if 1 <= pred <= 26:
                text = ptext + char
            elif pred in (27, 28, 29, 30):
                text = ptext.rstrip()
                # word = text[text.rfind(' ')+1:]
                # dic = enchant.Dict('en_US')
                # if not dic.check(word):
                #     self.process_invalid_message()
                #     return
                text += (', ' if pred == 27 else
                '? ' if pred == 28 else
                "'" if pred == 29 else
                ' ')
            elif 33 <= pred <= 37:
                if int(char) + 1 > len(self.words):
                    self.process_invalid_message()
                    return
                word = self.words[int(char)]
                text = ptext
                idx = text.rfind(' ')
                text = text[:idx+1] + word + ' '
            elif 38 <= pred <= 39:
                if int(char) - 4 > len(self.utterances):
                    self.process_invalid_message()
                    return
                text = ptext
                utterance_idx = max(text.rfind(p) for p in [', ', '? ', '. ', '! ', '; '])
                utterance_idx = -2 if utterance_idx == -1 else utterance_idx
                text = text[:utterance_idx+2] + self.utterances[int(char) - 5]
                text += ' ' if text[-1:] in [',', '?', '.', '!', ';'] else ''
            elif pred == 31:
                self.dialogue.undo()
                text = self.dialogue.undo()
            elif pred == 32:
                text = ptext.rstrip()
                idx = text.rfind(' ')
                text = text[:idx+1]
            elif pred == 40:
                self.stimulator.endRunFlag = True

                text = ptext
                # text = "Doctor-patient story"
                self.dialogue.setFormattedUtterance(['User', text])
                self.dialogueExp.setSampleUtterance(self.dialogue.getUtterance(), self.sample_idx)
                self.dialogueExp.addStoke(pred, self.sample_idx)
                self.dialogueExp.stopRunTime(self.sample_idx)
                self.dialogueExp.saveTestResults()

                message = {'state': mState.STATE_RESULT, 'server': 'chatbot', 'dialogue': self.dialogue.getFormattedDialogue()}
                self.tcpClient_chatbot.write(self.pack.pack(message))
                self.add_message(Ui_user_widget, self.dialogue.getUtteranceContent())

                self.words = []
                self.utterances = []
                self.lineEdit_1.setText('')
                self.lineEdit_2.clear()
                self.lineEdit_3.clear()
                return
            else:
                self.process_invalid_message()
                return

            # text = 'Apples are good for health, so i eat ap'
            self.dialogue.setText(text)
            self.dialogueExp.addStoke(pred, self.sample_idx)
            self.words = []
            self.utterances = []
            self.lineEdit_1.setText(text)
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            message = {'state': mState.STATE_RESULT, 'server': 'chatbot', 'dialogue': self.dialogue.getFormattedDialogue(), 'text': ["User", text]}
            self.tcpClient_chatbot.write(self.pack.pack(message))

        elif message['server'] == 'chatbot':
            if not self.messageDelayTimer.isActive():
                return
            self.messageDelayTimer.stop()
            if 'text' in message:
                self.words = message['words']
                self.utterances = message['utterances']
                self.text_words = ''
                for i in range(0, len(self.words)):
                    self.text_words += f"{i}. {self.words[i]}   "
                self.text_utterances = ''
                for i in range(5, 5 + len(self.utterances)):
                    self.text_utterances += f"{i}. {self.utterances[i - 5]}   "
                self.lineEdit_2.setText(self.text_words)
                self.lineEdit_3.setText(self.text_utterances)
                self.resume()
            else:
                self.dialogue.setFormattedUtterance(message['response'])
                chatbot_message_widget = self.add_message(Ui_chatbot_widget, '')

                response = self.dialogue.getUtteranceContent()
                token_integers = self.encoding.encode(response)
                tokens = [self.encoding.decode_single_token_bytes(token).decode() for token in token_integers]
                self.messageStreamTimer.timeout.connect(partial(self.on_messageStreamTimer_timeout, chatbot_message_widget, tokens))
                self.messageStreamTimer.start(100)

    def process_stimulation(self, stimulation: dict):
        state = stimulation['state']
        self.player.state = state
        self.player.setFocus()
        if state == mState.STATE_NULL:
            self.pause()
            self.sample_idx, dialogue_sample = self.dialogueExp.getOneSample()
            self.dialogue.clear()
            self.dialogue.setDialogue(dialogue_sample['context'])
            stimulation['server'] = 'decoder'
            self.tcpClient_decoder.write(self.pack.pack(stimulation))
            stimulation['server'] = 'chatbot'
            self.tcpClient_chatbot.write(self.pack.pack(stimulation))
            self.player.process(**stimulation)

            try:
                candidates = chat_input_completion_mode1(self.dialogue.getDialogue(), 'User: [< >]')
            except Exception as e:
                print(e)
                candidates = {'words': [], 'user utterances': []}
            self.words = candidates['words']
            self.utterances = candidates['user utterances']
            self.text_words = ''
            for i in range(0, len(self.words)):
                self.text_words += f"{i}. {self.words[i]}   "
            self.text_utterances = ''
            for i in range(5, 5 + len(self.utterances)):
                self.text_utterances += f"{i}. {self.utterances[i - 5]}   "
            self.lineEdit_2.setText(self.text_words)
            self.lineEdit_3.setText(self.text_utterances)

            self.clear_message()
            for role, message in self.dialogue.formatted_dialogue:
                MessageWidget = Ui_user_widget if role == 'User' else Ui_chatbot_widget
                self.add_message(MessageWidget, message)

        elif state == mState.STATE_STIMULI:
            stimulation['warm up'] = True
            self.wt = time.time()
            self.stimuliTimer.timeout.connect(partial(self.on_stimuliTimer_timeout, stimulation))
            self.stimuliTimer.start(mStateDur.STATE_STIMULI_STEP)
        elif state == mState.STATE_RESULT:
            self.pause()
            if self.stimulator.endRunFlag:
                stimulation['server'] = 'decoder'
                stimulation['pred'] = 40 # enter
                self.process_message(stimulation)
            else:
                if self.stimuliTimer.isActive():
                    self.stimuliTimer.stop()
                    self.stimuliTimer.disconnect()

                stimulation['server'] = 'decoder'
                self.tcpClient_decoder.write(self.pack.pack(stimulation))
                self.player.process(**stimulation)
            self.lineEdit_1.setFocus()
            self.messageDelayTimer.start(MAX_MESSAGE_DELAY)
            gc.collect()
        elif state == mState.STATE_TABLE:
            if stimulation['trial'] == 0:
                self.dialogueExp.startRunTime(self.sample_idx)
            self.player.process(**stimulation)
        else:
            pass

    def on_stimuliTimer_timeout(self, stimulation):
        if stimulation['state'] != self.player.state:
            return

        if stimulation['warm up']:
            if time.time() - self.wt > 0.1:
                stimulation['warm up'] = False

        s = time.time()
        #self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT | self.gl.GL_ACCUM_BUFFER_BIT | self.gl.GL_STENCIL_BUFFER_BIT)
        self.player.process(**stimulation)
        e = time.time()
        if e - s > 0.002 and e - self.wt < mStateDur.STATE_STIMULI_DUR and not stimulation['warm up']:
            print(f'dif {e-s}')
            print(f'time {e - self.wt}')

    def on_messageStreamTimer_timeout(self, messageWidget, message_tokens):
        if self.player.state == mState.STATE_RESULT:
            if len(message_tokens):
                token = message_tokens.pop(0)
                text = messageWidget.textBrowser.toPlainText()
                messageWidget.setText(text + token)
            else:
                self.messageStreamTimer.stop()
                self.messageStreamTimer.disconnect()
                self.resume()
        else:
            self.messageStreamTimer.stop()
            self.messageStreamTimer.disconnect()

    def on_messageDelayTimer_timeout(self):
        # only one can be activated between messageDelayTimer and process_message
        if self.player.state == mState.STATE_RESULT:
            if self.messageStreamTimer.isActive():
                return
            self.stimulator.trialTimeoutFlag = True
            self.resume()

    def on_scrollbar_rangeChanged(self):
        self.scrollbar.setValue(self.scrollbar.maximum())

    def add_message(self, MessageWidget, message):
        message_widget = createMessageClass(MessageWidget)(self.scrollAreaWidgetContents)
        message_widget.setText(message)
        self.verticalLayout.insertWidget(self.verticalLayout.count() - 1, message_widget)
        return message_widget

    def clear_message(self):
        item_list = list(range(self.verticalLayout.count()))
        item_list.reverse()
        for i in item_list:
            item = self.verticalLayout.itemAt(i)
            if item.widget():
                self.verticalLayout.removeItem(item)
                item.widget().deleteLater()

    def process_invalid_message(self):
        if self.player.state == mState.STATE_RESULT:
            if self.messageDelayTimer.isActive():
                self.messageDelayTimer.stop()
                self.stimulator.trialTimeoutFlag = True
                self.resume()

    def pause(self):
        # be cautious to use this function
        if self.isRunning:
            print(f'experiment pause')
            self.isRunning = False
            self.stimulator.mutex.lock()
            self.stimulator.event.set()
        if self.stimuliTimer.isActive():
            self.stimuliTimer.stop()
            self.stimuliTimer.disconnect()

    def resume(self):
        if not self.isRunning:
            print(f'experiment resume')
            self.isRunning = True
            self.stimulator.mutex.unlock()
            time.sleep(0.01)

    def keyReleaseEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Space and self.focusWidget() is self.player:
            if self.isRunning:
                self.pause()
            else:
                if self.player.state == mState.STATE_RESULT:
                    warnings.warn(f"Manually resume the stimulation thread at the RESULT state!")
                self.resume()
        elif a0.key() == Qt.Key.Key_Escape:
            self.close()
        a0.accept()

    def closeEvent(self, a0) -> None:
        self.stimulator.terminate()
        self.tcpClient_decoder.disconnect()
        self.tcpClient_chatbot.disconnect()
        a0.accept()


if __name__ == '__main__':
    scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Floor)

    format = QSurfaceFormat()
    format.setSwapInterval(0)
    format.setSwapBehavior(QSurfaceFormat.SwapBehavior.DefaultSwapBehavior)
    QSurfaceFormat.setDefaultFormat(format)

    app = QApplication([])
    client = Client()
    #client.showFullScreen()
    client.show()
    sys.exit(app.exec())