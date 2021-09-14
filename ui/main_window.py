# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_main(object):
    def setupUi(self, main):
        if not main.objectName():
            main.setObjectName(u"main")
        main.resize(800, 600)
        self.central_widget = QWidget(main)
        self.central_widget.setObjectName(u"central_widget")
        self.grid_layout_ = QGridLayout(self.central_widget)
        self.grid_layout_.setObjectName(u"grid_layout_")
        self.grid_layout = QGridLayout()
        self.grid_layout.setObjectName(u"grid_layout")
        self.label_filter = QLabel(self.central_widget)
        self.label_filter.setObjectName(u"label_filter")
        self.label_filter.setMinimumSize(QSize(30, 20))

        self.grid_layout.addWidget(self.label_filter, 1, 5, 1, 1)

        self.console = QTextBrowser(self.central_widget)
        self.console.setObjectName(u"console")
        self.console.setMinimumSize(QSize(400, 300))

        self.grid_layout.addWidget(self.console, 0, 0, 1, 7)

        self.filter_box = QComboBox(self.central_widget)
        self.filter_box.setObjectName(u"filter_box")
        self.filter_box.setMinimumSize(QSize(70, 20))

        self.grid_layout.addWidget(self.filter_box, 1, 6, 1, 1)

        self.username = QLineEdit(self.central_widget)
        self.username.setObjectName(u"username")
        self.username.setMinimumSize(QSize(100, 20))

        self.grid_layout.addWidget(self.username, 2, 0, 1, 1)

        self.version = QComboBox(self.central_widget)
        self.version.setObjectName(u"version")
        self.version.setMinimumSize(QSize(100, 20))

        self.grid_layout.addWidget(self.version, 3, 5, 1, 2)

        self.uuid = QLineEdit(self.central_widget)
        self.uuid.setObjectName(u"uuid")
        self.uuid.setMinimumSize(QSize(100, 20))

        self.grid_layout.addWidget(self.uuid, 2, 1, 1, 1)

        self.account_type = QComboBox(self.central_widget)
        self.account_type.setObjectName(u"account_type")
        self.account_type.setMinimumSize(QSize(100, 20))

        self.grid_layout.addWidget(self.account_type, 2, 5, 1, 2)

        self.button_options = QPushButton(self.central_widget)
        self.button_options.setObjectName(u"button_options")
        self.button_options.setMinimumSize(QSize(100, 20))

        self.grid_layout.addWidget(self.button_options, 2, 4, 1, 1)

        self.access_token = QLineEdit(self.central_widget)
        self.access_token.setObjectName(u"access_token")
        self.access_token.setMinimumSize(QSize(100, 20))

        self.grid_layout.addWidget(self.access_token, 2, 2, 1, 2)

        self.button_play = QPushButton(self.central_widget)
        self.button_play.setObjectName(u"button_play")
        self.button_play.setMinimumSize(QSize(300, 20))

        self.grid_layout.addWidget(self.button_play, 3, 0, 1, 5)

        self.progress_bar = QProgressBar(self.central_widget)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setMinimumSize(QSize(300, 20))
        self.progress_bar.setValue(0)

        self.grid_layout.addWidget(self.progress_bar, 1, 0, 1, 5)


        self.grid_layout_.addLayout(self.grid_layout, 0, 0, 1, 1)

        main.setCentralWidget(self.central_widget)
        self.status_bar = QStatusBar(main)
        self.status_bar.setObjectName(u"status_bar")
        main.setStatusBar(self.status_bar)

        self.retranslateUi(main)

        QMetaObject.connectSlotsByName(main)
    # setupUi

    def retranslateUi(self, main):
        main.setWindowTitle(QCoreApplication.translate("main", u"VILauncher", None))
        self.label_filter.setText(QCoreApplication.translate("main", u"Filter", None))
        self.username.setPlaceholderText(QCoreApplication.translate("main", u"Username", None))
        self.uuid.setPlaceholderText(QCoreApplication.translate("main", u"UUID", None))
        self.button_options.setText(QCoreApplication.translate("main", u"Options", None))
        self.access_token.setPlaceholderText(QCoreApplication.translate("main", u"Token", None))
        self.button_play.setText(QCoreApplication.translate("main", u"Play", None))
    # retranslateUi

