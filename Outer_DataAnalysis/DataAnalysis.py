# -- coding: utf-8 --
# 数据分析
import os
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from Outer_DataAnalysis.DataAnalysisWindow import Ui_MainWindow


class Main(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.file_dir = 'File_CSV'
        self.file_path = self.getFilePath()

    def getFilePath(self):
        return os.path.join(os.path.abspath(__file__).split('Outer')[0], self.file_dir)


def showMainWindow():
    app = QApplication(sys.argv)
    main_window = Main()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    showMainWindow()
