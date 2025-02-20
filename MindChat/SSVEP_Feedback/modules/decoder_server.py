from SSVEP_Feedback.cfg import *
import os
os.chdir(WORK_DIR)
import time
from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt6.QtWidgets import QMainWindow, QApplication
from utils.pylsl_inlet import CompositeInlet
from utils.tools import Depack, Pack
from SSVEP_Feedback.modules.decoder import Decoder
import pylsl
import sys
import copy
import random


class DecoderServer(QMainWindow):
    def __init__(self):
        super(DecoderServer, self).__init__()

        self.tcpServer = QTcpServer(self)
        self.clientConnection = QTcpSocket()
        self.tcpServer.listen(QHostAddress.SpecialAddress.LocalHost, IP_PORT_DECODER)
        assert self.tcpServer.isListening()
        self.depack = Depack()
        self.pack = Pack()

        self.streamInfo = [info for info in pylsl.resolve_streams() if info.type() == 'EEG' and info.name() == 'HA-2021.09.01'][0]
        self.compositeInlet = CompositeInlet(self.streamInfo)
        self.decoder = Decoder()

        self.initMetaData()
        self.initSingalSlot()

    def initMetaData(self):
        self.lsl_name = self.streamInfo.name()
        self.lsl_cn = self.streamInfo.channel_count()
        self.lsl_fs = self.streamInfo.nominal_srate()
        assert self.lsl_fs == FS

    def initSingalSlot(self):
        self.tcpServer.newConnection.connect(self.newConnect)

    def newConnect(self):
        self.clientConnection = self.tcpServer.nextPendingConnection()
        assert self.clientConnection.isOpen()
        self.clientConnection.readyRead.connect(self.readMessage)
        self.clientConnection.disconnected.connect(self.delConnect)

        # need reinitialization of inlet
        self.compositeInlet.inlet = pylsl.StreamInlet(self.streamInfo)
        self.compositeInlet.start()
        print('The client has been connected!')

    def delConnect(self):
        self.clientConnection.deleteLater()
        self.compositeInlet.stop()
        MODEL_QUEUE.clear()
        for i in range(RUN_NUM // len(MODEL_SET)):
            random.shuffle(MODEL_SET)
            MODEL_QUEUE.extend(MODEL_SET)
        print('The client has been disconnected!')

    def readMessage(self):
        if n := self.clientConnection.bytesAvailable():
            package = self.clientConnection.read(n)
            messages = self.depack.depack(package)
            for message in messages:
                self.process(message)

    def process(self, message: dict):
        if message['state'] == mState.STATE_RESULT:
            try:
                data = self.compositeInlet.get_data_by_marker(mState.STATE_STIMULI, *DATA_DUR)
                pred = self.decoder.process(data)
                message['pred'] = pred
                # message['pred'] = self.decoding_list.pop(0)
            except Exception as e:
                print(e)
                message['pred'] = -1
            self.clientConnection.write(self.pack.pack(message))
        elif message['state'] == mState.STATE_NULL:
            if MODEL_QUEUE:
                model = MODEL_QUEUE.pop(0)
                self.decoder.setModel(MODEL_PATH[model])
                message['model'] = model
            else:
                print('End of experiment!')
            #self.clientConnection.write(self.pack.pack(message))

    def closeEvent(self, a0) -> None:
        self.compositeInlet.stop()
        self.tcpServer.close()
        a0.accept()


if __name__ == '__main__':
    app = QApplication([])
    server = DecoderServer()
    server.show()
    #server.hide()
    sys.exit(app.exec())