# -- coding: utf-8 --
# 图像检测
import copy
import ctypes
import os
from dataclasses import dataclass

import cv2
import numpy as np

result = 0


class DetectionBase:
    """图像检测基类"""

    def __init__(self, cam_num=None):
        self.dll_dir = os.path.join(os.path.abspath('./'), "File_Static")
        self.dll_path = self.getDllPath()
        global x1, y1, x2, y2
        x1 = y1 = x2 = y2 = 0
        self.args_dict = {'SpinBox': {}, 'Coord': {}}
        # 是否开启动态库
        self.call_dll = self.callDll()
        self.dll = self.getDll()
        self.processFunction = self.getProcessFunction()

    def getDllPath(self):
        return os.path.join(self.dll_dir, os.path.basename(__file__).split(".")[0] + ".dll")

    def getDll(self):
        if self.call_dll:
            try:
                try:
                    dll = ctypes.WinDLL(self.dll_path, winmode=8)
                except:
                    dll = ctypes.WinDLL(self.dll_path)
                return dll
            except Exception as e:
                print(f"{e}\n动态库{self.dll_path}不存在!")
                return exit(6)

    @dataclass
    class Point:
        x: int
        y: int

    def getProcessFunction(self):
        if self.call_dll:

            return self.callCpp
        else:
            return self.processing

    def callCpp(self, img):

        height, width, channel = img.shape

        img_c_uchar_p = img.ctypes.data_as(ctypes.c_char_p)

        result = self.dll.getResults(img_c_uchar_p, height, width, channel)

        # img_string = ctypes.string_at(img_c_uchar_p, height * width * channel)

        # self.src = np.frombuffer(img_string, np.uint8).reshape(height, width, channel)

        return result

    def getProcessingResult(self, ndarray):
        """调用该方法 获取检测结果"""
        self.bgr = ndarray
        self.src = copy.deepcopy(ndarray)
        # noinspection PyArgumentList
        result = self.processFunction(self.src)
        return result, self.bgr, self.src

    def updateVariateToDll(self, variate):
        # 变量数组
        int_array = (ctypes.c_int * len(variate))(*variate.values())
        # 更新dll参数
        self.dll.updateArgs(int_array)

    def updateVariate(self):
        """调用该方法 更新变量值"""
        val_dict = self.args_dict['SpinBox']

        if self.call_dll:
            self.updateVariateToDll(val_dict)
        else:
            self.updateVariateToPy(val_dict)

    def updateCoord(self):
        """调用该方法 更新坐标变量"""
        coord_tuple = self.args_dict['Coord']
        if self.call_dll:
            self.updateCoordToDll(coord_tuple)
        else:
            self.updateCoordToPy(coord_tuple)

    def updateCoordToDll(self, coord_tuple):
        # 变量数组
        int_array = (ctypes.c_int * 4)(*coord_tuple)
        # 更新dll参数
        self.dll.updateCoord(int_array)

    def updateCoordToPy(self, coord_tuple):
        global Point_A, Point_B
        x1, y1, x2, y2 = coord_tuple
        Point_A = self.Point(x1, y1)
        Point_B = self.Point(x2, y2)

    @staticmethod
    def defErrorType():
        """定义错误类型"""
        error_type_dict = {
            # Todo 一、定义错误类型
            -1: '错误1',
            -2: '错误2',
            -3: '错误3',
        }
        return error_type_dict

    @staticmethod
    def defineParams():
        """定义参数: 参数名:[最大值,最小值,当前值] """
        params_dict = {
            # Todo 二、定义界面参数: ('参数名' :[最小值, 最大值, 当前值])
            '默认1': [0, 500, 1],
            '默认2': [0, 100, 1],
            '默认3': [0, 255, 1],
            # '默认4': [0, 200, 1],
            '默认5': [0, 200, 1],
        }
        return params_dict

    @staticmethod
    def callDll():
        # Todo 三、选择运行模式
        #  True  调用C动态库处理图像, 过程在process.processing()的Dll中实现, 后续步骤在 C++process 中完成.
        #  False 调用Python处理图像, 过程在当前类 processing()函数中实现, 后续步骤 向下 完成.

        call_dll = True
        # call_dll = False

        return call_dll

    # Todo Python设置: 启用python时有效 ##################################################################################

    @staticmethod
    def updateVariateToPy(variate):
        # Todo 四、根据界面参数 声明变量.
        global out_circle, in_circle, threshold, max_r, min_r

        # Todo 五、映射变量.
        out_circle = variate[0]
        in_circle = variate[1]
        threshold = variate[2]
        max_r = variate[3]
        # min_r = val_dict[4]

    def processing(self, img: np.ndarray) -> int:
        # Todo 六、在此处写图像算法:传入CV2.BGR彩图, 最后给 self.img(必须为3通道图) 或 self.src(可以为单通道图) 赋值以更新图像.
        #  提示: 训练区域坐标为Point类型的 Point_A(左上) 和  Point_B(右下)

        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY, img)

        print('--> Python Output Imagr <--')

        return result

    # Todo 完成 ########################################################################################################
