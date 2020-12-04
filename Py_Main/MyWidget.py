from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QLabel


class EventLabel(QLabel):
    """重写QLabel, 增加鼠标点击事件"""

    def __init__(self, Window):
        super().__init__(Window)
        self.draw_rect = self.flag = False
        self.x0 = self.y0 = self.x1 = self.y1 = 0
        self.x_min = self.y_min = self.x_max = self.y_max = 0

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.draw_rect:
            self.flag = True
            self.x0, self.y0 = event.x(), event.y()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.flag = False

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.draw_rect and self.flag:
            self.x1, self.y1 = event.x(), event.y()

            self.x_min = min(self.x0, self.x1)
            self.y_min = min(self.y0, self.y1)
            self.x_max = max(self.x0, self.x1)
            self.y_max = max(self.y0, self.y1)

            self.update()

    def paintEvent(self, event):
        """绘制事件"""
        super().paintEvent(event)

        rect = QRect(self.x_min, self.y_min, self.x_max - self.x_min, self.y_max - self.y_min)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.magenta, 1, Qt.DashLine))
        painter.drawRect(rect)

    def updateRect(self, x1, y1, x2, y2):
        """更新矩形"""
        self.x_min, self.y_min, self.x_max, self.y_max = x1, y1, x2, y2
        self.update()

    def setDrawRect(self, Bool: bool):
        """设置是否绘制矩形"""
        self.draw_rect = Bool

    def getCoord(self) -> tuple:
        """获取矩形区域坐标: x1,y1,x2,y2"""
        return self.x_min, self.y_min, self.x_max, self.y_max
