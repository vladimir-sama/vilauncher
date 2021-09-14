# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_dialog(object):
    def setupUi(self, dialog):
        if not dialog.objectName():
            dialog.setObjectName(u"dialog")
        dialog.resize(412, 300)
        self.grid_layout_ = QGridLayout(dialog)
        self.grid_layout_.setObjectName(u"grid_layout_")
        self.grid_layout_.setContentsMargins(-1, 9, -1, -1)
        self.button_box = QDialogButtonBox(dialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.grid_layout_.addWidget(self.button_box, 1, 0, 1, 1)

        self.grid_layout = QGridLayout()
        self.grid_layout.setObjectName(u"grid_layout")
        self.label_min_current = QLabel(dialog)
        self.label_min_current.setObjectName(u"label_min_current")
        self.label_min_current.setMinimumSize(QSize(20, 20))
        self.label_min_current.setAlignment(Qt.AlignCenter)

        self.grid_layout.addWidget(self.label_min_current, 0, 0, 1, 1)

        self.check_snapshots = QCheckBox(dialog)
        self.check_snapshots.setObjectName(u"check_snapshots")
        self.check_snapshots.setMinimumSize(QSize(360, 20))

        self.grid_layout.addWidget(self.check_snapshots, 3, 0, 1, 3)

        self.check_old = QCheckBox(dialog)
        self.check_old.setObjectName(u"check_old")
        self.check_old.setMinimumSize(QSize(360, 20))

        self.grid_layout.addWidget(self.check_old, 2, 0, 1, 3)

        self.slider_min_ram = QSlider(dialog)
        self.slider_min_ram.setObjectName(u"slider_min_ram")
        self.slider_min_ram.setMinimumSize(QSize(240, 20))
        self.slider_min_ram.setOrientation(Qt.Horizontal)

        self.grid_layout.addWidget(self.slider_min_ram, 0, 1, 1, 1)

        self.slider_max_ram = QSlider(dialog)
        self.slider_max_ram.setObjectName(u"slider_max_ram")
        self.slider_max_ram.setMinimumSize(QSize(240, 20))
        self.slider_max_ram.setOrientation(Qt.Horizontal)

        self.grid_layout.addWidget(self.slider_max_ram, 1, 1, 1, 1)

        self.label_min = QLabel(dialog)
        self.label_min.setObjectName(u"label_min")
        self.label_min.setMinimumSize(QSize(60, 20))

        self.grid_layout.addWidget(self.label_min, 0, 2, 1, 1)

        self.check_modified = QCheckBox(dialog)
        self.check_modified.setObjectName(u"check_modified")
        self.check_modified.setMinimumSize(QSize(360, 20))

        self.grid_layout.addWidget(self.check_modified, 4, 0, 1, 3)

        self.label_max = QLabel(dialog)
        self.label_max.setObjectName(u"label_max")
        self.label_max.setMinimumSize(QSize(60, 20))

        self.grid_layout.addWidget(self.label_max, 1, 2, 1, 1)

        self.label_max_current = QLabel(dialog)
        self.label_max_current.setObjectName(u"label_max_current")
        self.label_max_current.setMinimumSize(QSize(20, 20))
        self.label_max_current.setAlignment(Qt.AlignCenter)

        self.grid_layout.addWidget(self.label_max_current, 1, 0, 1, 1)

        self.jvm_args = QLineEdit(dialog)
        self.jvm_args.setObjectName(u"jvm_args")
        self.jvm_args.setMinimumSize(QSize(360, 20))

        self.grid_layout.addWidget(self.jvm_args, 6, 0, 1, 3)

        self.github_token = QLineEdit(dialog)
        self.github_token.setObjectName(u"github_token")

        self.grid_layout.addWidget(self.github_token, 5, 0, 1, 3)


        self.grid_layout_.addLayout(self.grid_layout, 0, 0, 1, 1)


        self.retranslateUi(dialog)
        # self.button_box.accepted.connect(dialog.accept)
        # self.button_box.rejected.connect(dialog.reject)

        QMetaObject.connectSlotsByName(dialog)
    # setupUi

    def retranslateUi(self, dialog):
        dialog.setWindowTitle(QCoreApplication.translate("dialog", u"Options", None))
        self.label_min_current.setText(QCoreApplication.translate("dialog", u"0", None))
        self.check_snapshots.setText(QCoreApplication.translate("dialog", u"Show snapshots", None))
        self.check_old.setText(QCoreApplication.translate("dialog", u"Show old versions", None))
        self.label_min.setText(QCoreApplication.translate("dialog", u"Min RAM", None))
        self.check_modified.setText(QCoreApplication.translate("dialog", u"Show modified", None))
        self.label_max.setText(QCoreApplication.translate("dialog", u"Max RAM", None))
        self.label_max_current.setText(QCoreApplication.translate("dialog", u"0", None))
        self.jvm_args.setPlaceholderText(QCoreApplication.translate("dialog", u"JVM Arguments", None))
        self.github_token.setPlaceholderText(QCoreApplication.translate("dialog", u"Github Access Token", None))
    # retranslateUi

