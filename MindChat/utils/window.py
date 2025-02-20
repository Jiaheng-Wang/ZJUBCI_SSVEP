# Form implementation generated from reading ui file 'window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(924, 564)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(parent=Form)
        self.frame.setMinimumSize(QtCore.QSize(500, 0))
        self.frame.setStyleSheet("QFrame{\n"
"border: 2px solid #a0a0a0;\n"
"border-radius: 10px;\n"
"}")
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.frame.setLineWidth(2)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget = QtWidgets.QWidget(parent=self.frame)
        self.widget.setStyleSheet("background-color: rgb(160, 160, 160);")
        self.widget.setObjectName("widget")
        self.verticalLayout_2.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(parent=self.frame)
        self.widget_2.setMinimumSize(QtCore.QSize(0, 50))
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 50))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_1 = QtWidgets.QLineEdit(parent=self.widget_2)
        self.lineEdit_1.setMinimumSize(QtCore.QSize(0, 50))
        self.lineEdit_1.setMaximumSize(QtCore.QSize(16777215, 50))
        self.lineEdit_1.setStyleSheet("font: 13pt \"微软雅黑\";\n"
"border: 2px solid #55aaff;\n"
"border-bottom-width: 1px;\n"
"border-bottom-color: rgba(85, 170, 255, 125);\n"
"border-right-width: 0px;\n"
"")
        self.lineEdit_1.setText("")
        self.lineEdit_1.setFrame(True)
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.horizontalLayout_2.addWidget(self.lineEdit_1)
        self.label = QtWidgets.QLabel(parent=self.widget_2)
        self.label.setMinimumSize(QtCore.QSize(150, 50))
        self.label.setMaximumSize(QtCore.QSize(150, 50))
        self.label.setStyleSheet("border: 2px solid #55aaff;\n"
"border-radius: 0px;\n"
"border-bottom-width: 1px;\n"
"border-bottom-color: rgba(85, 170, 255, 125);\n"
"border-left-width: 0px;\n"
"background-color: rgb(255, 255, 255);")
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/image/logo.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.verticalLayout_2.addWidget(self.widget_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.frame)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(0, 50))
        self.lineEdit_2.setMaximumSize(QtCore.QSize(16777215, 50))
        self.lineEdit_2.setStyleSheet("font: 13pt \"微软雅黑\";\n"
"border: 2px solid #55aaff;\n"
"border-top-width: 0px;\n"
"border-bottom-width: 1px;\n"
"border-bottom-color: rgba(85, 170, 255, 125);")
        self.lineEdit_2.setText("")
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setClearButtonEnabled(False)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout_2.addWidget(self.lineEdit_2)
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.frame)
        self.lineEdit_3.setMinimumSize(QtCore.QSize(0, 50))
        self.lineEdit_3.setMaximumSize(QtCore.QSize(16777215, 50))
        self.lineEdit_3.setStyleSheet("font: 11pt \"微软雅黑\";\n"
"border: 2px solid #55aaff;\n"
"border-top-width: 0px;")
        self.lineEdit_3.setText("")
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.verticalLayout_2.addWidget(self.lineEdit_3)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(parent=Form)
        self.scrollArea.setMinimumSize(QtCore.QSize(400, 400))
        self.scrollArea.setMaximumSize(QtCore.QSize(400, 16777215))
        self.scrollArea.setStyleSheet("QScrollArea{\n"
"border: 2px solid #a0a0a0;\n"
"border-radius: 10px;\n"
"}\n"
"")
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 396, 542))
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(0, 0))
        self.scrollAreaWidgetContents.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.scrollAreaWidgetContents.setStyleSheet("background-color: #f5f5f5;\n"
"")
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 1000, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.lineEdit_1.setPlaceholderText(_translate("Form", "start a conversation"))
        self.lineEdit_2.setPlaceholderText(_translate("Form", "word list"))
        self.lineEdit_3.setPlaceholderText(_translate("Form", "utterance list"))

import ui_image_rc

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QWidget()
    Ui_Form().setupUi(win)
    win.show()
    app.exec()