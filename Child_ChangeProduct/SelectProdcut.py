# -- coding: utf-8 --
# 产品选择
from PyQt5.QtWidgets import QDialog

from Child_ChangeProduct.SelectProductWindow import Ui_Form

restart = None


class SelectProduct(Ui_Form, QDialog):
    def __init__(self, config_ini_path, config_ini_obj):
        global restart
        restart = False
        super(SelectProduct, self).__init__()
        # 引入GUI的setupUi
        self.setupUi(self)
        self.config_ini_path = config_ini_path
        self.config_ini_obj = config_ini_obj
        self.former_index = 0
        # 配置文件: 产品列表
        self.plist = self.config_ini_obj['product']['list']
        self.title = self.config_ini_obj['product']['title']
        self.setComboBoxItem()

        self.pushButton_1.clicked.connect(self.saveSet)
        self.pushButton_2.clicked.connect(self.cancelSet)

    def setComboBoxItem(self):
        self.product_list = [item.strip() for item in self.plist.split(',')]
        self.comboBox_0.clear()
        self.comboBox_0.addItems(self.product_list)

        for i, item, in enumerate(self.product_list):
            if item == self.title.strip():
                self.former_index = i
                break
        self.comboBox_0.setCurrentIndex(self.former_index)

        self.label_0.setText('当前产品: %s' % self.product_list[self.former_index])

    def saveSet(self):
        """保存设置"""
        global restart
        current_index = self.comboBox_0.currentIndex()

        if current_index != self.former_index:
            self.config_ini_obj['product']['title'] = self.product_list[current_index]
            with open(self.config_ini_path, 'w', encoding='utf8') as f:
                self.config_ini_obj.write(f)
            print('保存配置文件成功~')
            restart = True
        self.close()

    def cancelSet(self):
        """取消设置"""
        global restart
        restart = False
        self.close()


def showSelectProductWindow(config_ini_path, config_ini_obj):
    select_product_window = SelectProduct(config_ini_path, config_ini_obj)
    select_product_window.exec()
    return restart
