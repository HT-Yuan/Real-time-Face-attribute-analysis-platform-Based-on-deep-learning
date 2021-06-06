# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/huatsing/Desktop/pyqt/last.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
# import cv2
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Title_lable = QtWidgets.QLabel(self.centralwidget)
        self.Title_lable.setGeometry(QtCore.QRect(0, 0, 791, 41))
        self.Title_lable.setObjectName("Title_lable")
        self.Main_Frame = QtWidgets.QGraphicsView(self.centralwidget)
        self.Main_Frame.setGeometry(QtCore.QRect(0, 30, 661, 531))
        self.Main_Frame.setObjectName("Main_Frame")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(660, 30, 231, 531))
        self.textBrowser.setObjectName("textBrowser")
        self.ON_OFF = QtWidgets.QPushButton(self.centralwidget)
        self.ON_OFF.setGeometry(QtCore.QRect(930, 170, 80, 23))
        self.ON_OFF.setObjectName("ON_OFF")
        self.data_boottom = QtWidgets.QPushButton(self.centralwidget)
        self.data_boottom.setGeometry(QtCore.QRect(930, 220, 80, 23))
        self.data_boottom.setObjectName("data_boottom")
        self.expression_bottom = QtWidgets.QPushButton(self.centralwidget)
        self.expression_bottom.setGeometry(QtCore.QRect(930, 270, 80, 23))
        self.expression_bottom.setObjectName("expression_bottom")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1024, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Title_lable.setText(_translate("MainWindow", "TITLE                            -- BY Hty"))
        self.ON_OFF.setText(_translate("MainWindow", "ON/OFF"))
        self.data_boottom.setText(_translate("MainWindow", "历史数据"))
        self.expression_bottom.setText(_translate("MainWindow", "表情识别"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())

