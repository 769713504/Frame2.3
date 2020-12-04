# -- coding: utf-8 --
# 异常图像浏览
import os

from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog

from Child_ExceptionImage.ExceptionImageWindow import Ui_Form

restart = None


class ExceptionImage(Ui_Form, QDialog):
    def __init__(self, exception_dir):
        super(ExceptionImage, self).__init__()
        global restart
        restart = False
        # 继承GUI
        self.setupUi(self)
        # 设置ICO图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./File_Static/front.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_1.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap("./File_Static/next.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon)

        # 异常图片目录路径
        self.abnormal_path = exception_dir
        # 异常图片列表
        self.abnormal_image_list = self.getAbnormalImageList()
        # 异常图数量
        self.total = len(self.abnormal_image_list)
        # 当前编号
        self.now_mun = 0
        # 显示第一张图
        self.showAbnormalImageToLabel()

        # 普通按钮
        self.pushButton_1.clicked.connect(self.showFrontImage)  # 上一个
        self.pushButton_2.clicked.connect(self.showNextImage)  # 下一个

    def showFrontImage(self):
        self.now_mun -= 1
        self.showAbnormalImageToLabel()

    def showNextImage(self):
        self.now_mun += 1
        self.showAbnormalImageToLabel()

    def showAbnormalImageToLabel(self):
        # 显示
        try:
            img_path = self.abnormal_image_list[self.now_mun]
            Qimg = QtGui.QPixmap(img_path).scaled(self.label_1.width(), self.label_1.height())
            self.label_1.setPixmap(Qimg)
            self.label_2.setText(f"{self.now_mun + 1}/{self.total}")
        except Exception as e:
            print(e)
        # 上一张
        if self.now_mun - 1 >= 0:
            self.pushButton_1.setEnabled(True)
        else:
            self.pushButton_1.setEnabled(False)
        # 下一张
        if self.now_mun + 1 < self.total:
            self.pushButton_2.setEnabled(True)
        else:
            self.pushButton_2.setEnabled(False)

    def getAbnormalImageList(self):
        return [os.path.join(self.abnormal_path, item) for item in os.listdir(self.abnormal_path)
                if item.split('.')[-1] in ['bmp', 'jpg']]
