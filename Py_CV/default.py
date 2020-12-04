# -- coding: utf-8 --
# 图像检测具体实现
from Py_Main.Inspection import *


class VisualDetection(DetectionBase):
    """视觉检测类"""

    def getDllPath(self):
        return os.path.join(self.dll_dir, os.path.basename(__file__).split(".")[0] + ".dll")

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
