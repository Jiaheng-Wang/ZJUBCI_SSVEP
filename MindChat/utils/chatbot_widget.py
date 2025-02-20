# Form implementation generated from reading ui file 'chatbot_widget.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_chatbot_widget(object):
    def setupUi(self, chatbot_widget):
        chatbot_widget.setObjectName("chatbot_widget")
        chatbot_widget.resize(350, 109)
        chatbot_widget.setMinimumSize(QtCore.QSize(0, 0))
        chatbot_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLayout = QtWidgets.QHBoxLayout(chatbot_widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.chatbot_icon = QtWidgets.QLabel(parent=chatbot_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chatbot_icon.sizePolicy().hasHeightForWidth())
        self.chatbot_icon.setSizePolicy(sizePolicy)
        self.chatbot_icon.setMinimumSize(QtCore.QSize(40, 40))
        self.chatbot_icon.setMaximumSize(QtCore.QSize(40, 40))
        self.chatbot_icon.setStyleSheet("")
        self.chatbot_icon.setText("")
        self.chatbot_icon.setPixmap(QtGui.QPixmap(":/image/chatbot.png"))
        self.chatbot_icon.setScaledContents(True)
        self.chatbot_icon.setObjectName("chatbot_icon")
        self.horizontalLayout.addWidget(self.chatbot_icon)
        self.textBrowser = QtWidgets.QTextBrowser(parent=chatbot_widget)
        self.textBrowser.setMinimumSize(QtCore.QSize(0, 0))
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.textBrowser.setStyleSheet("border: 1px solid rgba(85,255,127, 25);\n"
"border-radius: 20px;\n"
"background-color: rgba(85,255,127, 25);\n"
"padding:10px;\n"
"\n"
"")
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textBrowser.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.textBrowser.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
        self.textBrowser.setTabStopDistance(80.0)
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout.addWidget(self.textBrowser)
        spacerItem = QtWidgets.QSpacerItem(186, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(chatbot_widget)
        QtCore.QMetaObject.connectSlotsByName(chatbot_widget)

    def retranslateUi(self, chatbot_widget):
        _translate = QtCore.QCoreApplication.translate
        chatbot_widget.setWindowTitle(_translate("chatbot_widget", "Form"))
        self.textBrowser.setHtml(_translate("chatbot_widget", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:\'Microsoft YaHei UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Times New Roman\'; font-size:12pt;\"> </span></p></body></html>"))

import ui_image_rc

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QWidget()
    Ui_chatbot_widget().setupUi(win)
    win.show()
    app.exec()