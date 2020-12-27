# -- coding: utf-8 --
# 系统配置
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QDialog
from serial.tools import list_ports

from Child_SystemConfig.SystemConfigWindow import Ui_Form

restart = None


class SystemConfig(Ui_Form, QDialog):
    def __init__(self, config_ini_path, config_ini_obj):
        global restart
        restart = False
        super(SystemConfig, self).__init__()
        # 引入GUI的setupUi
        self.setupUi(self)
        # 系统配置文件路径
        self.config_ini_path = config_ini_path
        # 系统配置文件对象
        self.config_ini_obj = config_ini_obj
        # 记录密码是否更改
        self.user_password = None
        self.admin_password = None
        # 获取系统配置参数
        self.getSysConfigArgs()
        self.setSpinBox_0()

        self.comboBox_0.currentIndexChanged.connect(self.setSpinBox_0)
        # 点击事件
        self.pushButton_1.clicked.connect(self.saveSet)  # 保存参数
        self.pushButton_2.clicked.connect(self.cancelSet)  # 取消操作
        self.pushButton_3.clicked.connect(self.modifyUserPassword)  # 修改用户密码
        self.pushButton_4.clicked.connect(self.modifyAdminPassword)  # 修改管理员密码

    def setSpinBox_0(self):
        if self.comboBox_0.currentIndex() == 2:
            self.spinBox_0.setEnabled(True)
            self.comboBox_1.setEnabled(False)
        else:
            self.spinBox_0.setEnabled(False)
            self.comboBox_1.setEnabled(True)

    def modifyUserPassword(self):
        # 第三个参数表示显示类型，可选，有正常（QLineEdit.Normal）、密碼（ QLineEdit. Password）、不显示（ QLineEdit. NoEcho）三种情况
        value, ok = QInputDialog.getText(self, "用户密码", "请输入1~6位字符", QLineEdit.Password, '6')
        if ok:
            if len(value) > 6:
                if QMessageBox.warning(self, "无效密码!", "密码必须是1~6位字符!\n是否重新设置密码?",
                                       QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    return self.change_user_password()
            else:
                self.user_password = value

    def modifyAdminPassword(self):
        value, ok = QInputDialog.getText(self, "管理密码", "请输入1~6位字符", QLineEdit.Password, '6')
        if ok:
            if len(value) > 6:
                if QMessageBox.warning(self, "无效密码!", "密码必须是1~6位字符!\n是否重新设置密码?",
                                       QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    return self.change_admin_password()
            else:
                self.admin_password = value

    def disablecomboBox(self):
        if self.checkBox_0.isChecked():
            self.comboBox_0.setEnabled(False)
        else:
            self.comboBox_0.setEnabled(True)

    def setComboBox(self):
        self.comboBox_0.clear()
        self.comboBox_0.addItems([str(i) for i in range(self.cam_sum)])
        self.comboBox_0.setCurrentIndex(self.cam_num)

    def setPort(self):
        port_obj_list = list_ports.comports()
        port_name_list = [each_port[0].upper() for each_port in port_obj_list] if port_obj_list else []
        port = self.config_ini_obj.get('control', 'port').upper()

        if port in port_name_list:
            self.port_index = port_name_list.index(port)
        else:
            port_name_list.insert(0, f'{port}(不可用)')
            self.port_index = 0
        self.comboBox_1.addItems(port_name_list)
        self.comboBox_1.setCurrentIndex(self.port_index)

    def getSysConfigArgs(self):
        # 读取系统配置参数
        run_mode = self.config_ini_obj.getint('main', 'mode')
        cam_sum = self.config_ini_obj.getint('simulate', 'cam_sum')

        # 写入弹窗
        self.comboBox_0.setCurrentIndex(run_mode)
        self.setPort()
        self.spinBox_0.setValue(cam_sum)

    def setSysConfigArgs(self):
        global restart
        if self.user_password:
            self.config_ini_obj['password']['user'] = self.user_password
        if self.admin_password:
            self.config_ini_obj['password']['admin'] = self.admin_password
        if self.config_ini_obj['main']['mode'] != str(self.comboBox_0.currentIndex()):
            self.config_ini_obj['main']['mode'] = str(self.comboBox_0.currentIndex())
            restart = True
        if self.config_ini_obj['simulate']['cam_sum'] != str(self.spinBox_0.value()):
            self.config_ini_obj['simulate']['cam_sum'] = str(self.spinBox_0.value())
            restart = True
        if self.port_index != self.comboBox_1.currentIndex():
            self.config_ini_obj['control']['port'] = self.comboBox_1.currentText()
            restart = True
        print('参数设置成功~')

    def writeSysConfigFile(self):
        with open(self.config_ini_path, 'w', encoding='utf8') as f:
            self.config_ini_obj.write(f)
        print('保存配置文件成功~')

    def saveSet(self):
        """保存设置"""
        self.setSysConfigArgs()
        self.writeSysConfigFile()
        self.close()

    def cancelSet(self):
        """取消设置"""
        self.close()


def showSystemConfigWindow(config_ini_path, config_ini_obj):
    system_config_window = SystemConfig(config_ini_path, config_ini_obj)
    system_config_window.exec()
    return restart
