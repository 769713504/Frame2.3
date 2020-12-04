# -- coding: utf-8 --
# 系统配置
from PyQt5.QtWidgets import QDialog, QFileDialog

from Child_SaveMode.SaveModeWindow import Ui_Form

restart = None


class SaveMode(Ui_Form, QDialog):
    def __init__(self, config_ini_path, config_ini_obj):
        global restart
        restart = False
        super(SaveMode, self).__init__()
        # 引入GUI的setupUi
        self.setupUi(self)
        # 系统配置文件路径
        self.config_ini_path = config_ini_path
        # 系统配置文件对象
        self.config_ini_obj = config_ini_obj

        # 获取系统配置参数
        self.getSysConfigArgs()

        # 点击事件
        self.pushButton_0.clicked.connect(self.selectSaveDirectory)  # 打开目录
        self.pushButton_1.clicked.connect(self.saveSet)  # 保存参数
        self.pushButton_2.clicked.connect(self.cancelSet)  # 取消操作

    def selectSaveDirectory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选取文件夹", self.save_path)
        if dir_path and dir_path != self.save_path:
            self.save_path = dir_path

    def getSysConfigArgs(self):
        # 读取系统配置参数

        self.save_path = self.config_ini_obj.get('save', 'path')
        # 写入弹窗
        self.comboBox_1.setCurrentIndex(self.config_ini_obj.getint('save', 'mode'))
        self.comboBox_2.setCurrentIndex(self.config_ini_obj.getint('save', 'type'))

    def setSysConfigArgs(self):
        global restart
        if self.config_ini_obj['save']['mode'] != str(self.comboBox_1.currentIndex()):
            self.config_ini_obj['save']['mode'] = str(self.comboBox_1.currentIndex())
            restart = True
        if self.config_ini_obj['save']['type'] != str(self.comboBox_2.currentIndex()):
            self.config_ini_obj['save']['type'] = str(self.comboBox_2.currentIndex())
            restart = True
        if self.config_ini_obj['save']['path'] != self.save_path:
            self.config_ini_obj['save']['path'] = self.save_path
            restart = True

    def saveSet(self):
        """保存设置"""
        self.setSysConfigArgs()
        self.close()

    def cancelSet(self):
        """取消设置"""
        self.close()


def showSaveModeWindow(config_ini_path, config_ini_obj):
    save_mode_window = SaveMode(config_ini_path, config_ini_obj)
    save_mode_window.exec()
    return restart
