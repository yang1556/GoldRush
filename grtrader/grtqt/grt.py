# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'grt.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.kline_widget = QtWidgets.QWidget(self.centralwidget)
        self.kline_widget.setGeometry(QtCore.QRect(40, 30, 601, 311))
        self.kline_widget.setStyleSheet("background-color: rgb(7, 7, 7);\n"
"border: 1px solid;\n"
"border-color: rgb(60, 60, 60);\n"
"border-left-width: 0px;")
        self.kline_widget.setObjectName("kline_widget")
        self.x_label = QtWidgets.QLabel(self.kline_widget)
        self.x_label.setGeometry(QtCore.QRect(40, 290, 72, 15))
        self.x_label.setObjectName("x_label")
        self.y_label = QtWidgets.QLabel(self.kline_widget)
        self.y_label.setGeometry(QtCore.QRect(0, 200, 16, 61))
        self.y_label.setObjectName("y_label")
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setGeometry(QtCore.QRect(40, 360, 601, 81))
        self.widget_2.setStyleSheet("background-color: rgb(7, 7, 7);\n"
"border: 1px solid;\n"
"border-color: rgb(60, 60, 60);\n"
"border-left-width: 0px;")
        self.widget_2.setObjectName("widget_2")
        self.widget_3 = QtWidgets.QWidget(self.widget_2)
        self.widget_3.setGeometry(QtCore.QRect(0, 80, 601, 101))
        self.widget_3.setObjectName("widget_3")
        self.label = QtWidgets.QLabel(self.widget_3)
        self.label.setGeometry(QtCore.QRect(0, 0, 72, 15))
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(0, 27, 41, 71))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(0, 90, 41, 71))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(0, 160, 41, 71))
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 440, 601, 20))
        self.label_2.setObjectName("label_2")
        self.widget_4 = QtWidgets.QWidget(self.centralwidget)
        self.widget_4.setGeometry(QtCore.QRect(40, 460, 601, 81))
        self.widget_4.setStyleSheet("background-color: rgb(7, 7, 7);\n"
"border: 1px solid;\n"
"border-color: rgb(60, 60, 60);\n"
"border-left-width: 0px;")
        self.widget_4.setObjectName("widget_4")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(40, 340, 601, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(41, 10, 601, 20))
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
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
        self.x_label.setText(_translate("MainWindow", "TextLabel"))
        self.y_label.setText(_translate("MainWindow", "TextLabel"))
        self.label.setText(_translate("MainWindow", "TextLabel"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.pushButton_2.setText(_translate("MainWindow", "PushButton"))
        self.pushButton_3.setText(_translate("MainWindow", "PushButton"))
        self.label_2.setText(_translate("MainWindow", "TextLabel"))
        self.label_3.setText(_translate("MainWindow", "TextLabel"))
        self.label_4.setText(_translate("MainWindow", "TextLabel"))
