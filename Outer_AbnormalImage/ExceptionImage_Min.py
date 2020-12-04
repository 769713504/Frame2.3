# -- coding: utf-8 --
# 显示错误图像
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from Outer_AbnormalImage.ExceptionImage_MinWindow import Ui_MainWindow


class Main(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        # 引入Ui
        self.setupUi(self)


def showMainWindow():
    app = QApplication(sys.argv)
    main_window = Main()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    showMainWindow()
