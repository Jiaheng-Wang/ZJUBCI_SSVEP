import time
from SSVEP_Feedback.cfg import *
import os
os.chdir(WORK_DIR)
import re
from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt6.QtWidgets import QMainWindow, QApplication
from utils.tools import Depack, Pack
from utils.openai_api import chat_input_completion_mode1, chat_input_completion_mode2, get_word_completer, chat_response
import sys


class ChatbotServer(QMainWindow):
    def __init__(self):
        super(ChatbotServer, self).__init__()

        self.tcpServer = QTcpServer(self)
        self.clientConnection = QTcpSocket()
        self.tcpServer.listen(QHostAddress.SpecialAddress.AnyIPv4, IP_PORT_CHATBOT)
        assert self.tcpServer.isListening()
        self.depack = Depack()
        self.pack = Pack()
        self.word_completer = get_word_completer()

        self.initMetaData()
        self.initSingalSlot()

    def initMetaData(self):
        pass

    def initSingalSlot(self):
        self.tcpServer.newConnection.connect(self.newConnect)

    def newConnect(self):
        self.clientConnection = self.tcpServer.nextPendingConnection()
        assert self.clientConnection.isOpen()
        self.clientConnection.readyRead.connect(self.readMessage)
        self.clientConnection.disconnected.connect(self.delConnect)
        print('The client has been connected!')

    def delConnect(self):
        self.clientConnection.deleteLater()
        print('The client has been disconnected!')

    def readMessage(self):
        if n := self.clientConnection.bytesAvailable():
            package = self.clientConnection.read(n)
            messages = self.depack.depack(package)
            for message in messages:
                self.process(message)

    def process(self, message: dict):
        if message['state'] == mState.STATE_RESULT:
            st = time.time()
            try:
                if 'text' in message:
                    # message['phrases'] = self.phrases_list + [f'{time.time():.0f}']
                    # message['sentences'] = self.sentences_list'
                    context = "\n".join(": ".join(m) for m in message['dialogue']) + '\n'
                    role, text = message['text']
                    word_idx = text.rfind(" ")
                    prefix = text[word_idx + 1:]
                    text = text[:word_idx + 1] + '<' + (prefix if prefix else ' ') + '>'
                    sentence_idx = max(text.rfind(p) for p in [', ', '? ', '. ', '! ', '; '])
                    sentence_idx = -2 if sentence_idx == -1 else sentence_idx
                    text = role + ': ' + text[:sentence_idx + 2] + '[' + text[sentence_idx + 2:] + ']'
                    if CHAT_INPUT_MODE == 1:
                        candidates = chat_input_completion_mode1(context, text)
                    else:
                        candidates = chat_input_completion_mode2(context, text, self.word_completer)
                    message['words'] = [word.strip() for word in candidates['words']]
                    message['utterances'] = [re.sub("[\[\]<>]", "", sentence).strip() for sentence in candidates['user utterances']]
                elif 'dialogue' in message:
                    response = chat_response("\n".join(": ".join(m) for m in message['dialogue']))
                    message['response'] = ['Interlocutor', response.strip()]
            except Exception as e:
                print(e)
                if 'text' in message:
                    message['words'] = []
                    message['utterances'] = []
                else:
                    message['response'] = ['Interlocutor', 'Chat failure! Please try again!']
                return
            if time.time() - st <= MAX_MESSAGE_DELAY/1000 - 1:
                self.clientConnection.write(self.pack.pack(message))

        elif message['state'] == mState.STATE_NULL:
            pass

    def closeEvent(self, a0) -> None:
        self.tcpServer.close()
        a0.accept()


if __name__ == '__main__':
    app = QApplication([])
    server = ChatbotServer()
    server.show()
    #server.hide()
    sys.exit(app.exec())