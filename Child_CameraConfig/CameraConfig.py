# -- coding: utf-8 --
# 相机配置
from PyQt5.QtWidgets import QDialog

from Child_CameraConfig.CameraConfigWindow import Ui_Form

restart = None


class CameraConfig(Ui_Form, QDialog):
    def __init__(self, cam_sum, cam_num, cam_ini_obj_list):
        global restart
        restart = False
        super(CameraConfig, self).__init__()
        # 引入GUI的setupUi
        self.setupUi(self)
        # 相机数量
        self.cam_sum = cam_sum
        # 当前相机编号
        self.cam_num = cam_num
        # 相机配置文件对象列表
        self.cam_ini_obj_list = cam_ini_obj_list
        # 设置下拉表单
        self.setComboBox()
        # 获取当前相机参数
        self.getNowCamArgs()

        # 点击事件
        self.checkBox_0.clicked.connect(self.disablecomboBox)  # 复选
        self.pushButton_1.clicked.connect(self.saveSet)  # 保存参数
        self.pushButton_2.clicked.connect(self.cancelSet)  # 取消操作

    def disablecomboBox(self):
        if self.checkBox_0.isChecked():
            self.comboBox_0.setEnabled(False)
        else:
            self.comboBox_0.setEnabled(True)

    def setComboBox(self):
        self.comboBox_0.clear()
        self.comboBox_0.addItems([str(i) for i in range(self.cam_sum)])
        self.comboBox_0.setCurrentIndex(self.cam_num)

    def getNowCamArgs(self):
        args_dict = self.cam_ini_obj_list[self.cam_num]
        # 读取当前相机参数
        exposuretime = args_dict.getint('camera', 'exposuretime')  # 曝光时间
        framerate = args_dict.getint('camera', 'framerate')  # 帧率
        gain = args_dict.getint('camera', 'gain')  # 图像增益
        # 写入spinBox
        self.spinBox_1.setValue(exposuretime)
        self.spinBox_2.setValue(framerate)
        self.spinBox_3.setValue(gain)
        print('获取相机参数成功~')

    def setCamConfigArgs(self):
        """保存相机参数到对象"""
        global restart
        # 获取参数
        exposuretime = self.spinBox_1.value()  # 曝光时间
        framerate = self.spinBox_2.value()  # 帧率
        gain = self.spinBox_3.value()  # 图像增益

        # 判断复选框状态
        if self.checkBox_0.isChecked():
            restart = True
            for cam_ini_obj in self.cam_ini_obj_list:
                cam_ini_obj['camera']['exposuretime'] = str(exposuretime)
                cam_ini_obj['camera']['framerate'] = str(framerate)
                cam_ini_obj['camera']['gain'] = str(gain)
            print('所有相机参数已更新成功~')
        else:
            cam_ini_obj = self.cam_ini_obj_list[self.comboBox_0.currentIndex()]
            if cam_ini_obj['camera']['exposuretime'] != str(exposuretime):
                cam_ini_obj['camera']['exposuretime'] = str(exposuretime)
                restart = True
            if cam_ini_obj['camera']['framerate'] != str(framerate):
                cam_ini_obj['camera']['framerate'] = str(framerate)
                restart = True
            if cam_ini_obj['camera']['gain'] != str(gain):
                cam_ini_obj['camera']['gain'] = str(gain)
                restart = True
            if restart:
                print('相机%s参数已更新成功~' % self.comboBox_0.currentIndex())

    def saveSet(self):
        """保存设置"""
        self.setCamConfigArgs()
        self.close()

    def cancelSet(self):
        """取消设置"""
        self.close()


def showCameraConfigWindow(cam_sum, cam_num, cam_ini_obj_list):
    camera_config_window = CameraConfig(cam_sum, cam_num, cam_ini_obj_list)
    camera_config_window.exec()
    return restart
