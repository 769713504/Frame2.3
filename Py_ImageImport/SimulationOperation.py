import ctypes
import inspect
import os
import time
from threading import Thread

import cv2
from PyQt5.QtGui import QPixmap, QImage


class SimulationOperation:
    """模拟操作类"""

    def __init__(self,
                 cam_num,  # 相机编号
                 label_obj_dict,  # 列表对象字典
                 image_path_list,  # 图像路径列表
                 show_image_control_list,  # 显示图的控制列表
                 visual_detection_class_obj,  # 图像检测类
                 exception_path,  # 异常图片目录
                 cache_image_list,  # 缓存图像列表
                 control_dict,  # 控制字典
                 save_image_mode_dict,  # 保存图像模式的字典
                 errorStop_CallbackFunction,  # 回调函数:出错暂停
                 all_camera_result_text_dict,  # 缓存结果的字典
                 ):
        self.cam_num = cam_num
        # 标签对象
        self.label_main = label_obj_dict['label_main']
        self.label_error = label_obj_dict['label_error']
        self.label_info = label_obj_dict['label_info']
        self.label_result = label_obj_dict['label_result']
        # 图片路径列表
        self.image_path_list = image_path_list

        self.show_image_control_list = show_image_control_list
        self.image_detect_class_obj = visual_detection_class_obj
        # 异常图片目录路径
        self.exception_path = exception_path
        # 缓存图片列表
        self.cache_image_list = cache_image_list
        # 控制字典  {'Rejector': False, 'ErrorStop': False}
        self.control_dict = control_dict
        # 错误类型字典
        self.error_type_dict = visual_detection_class_obj.defErrorType()
        # 保存图像模式的字典
        self.save_image_mode_dict = save_image_mode_dict
        # 出错暂停的回调函数
        self.errorStop_CallbackFunction = errorStop_CallbackFunction
        # 当前相机缓存结果的字典
        self.all_camera_result_text_dict = all_camera_result_text_dict
        # 窗口宽高
        self.label_main_width, self.label_main_height = self.label_main.width(), self.label_main.height()
        # 读取对错图对象
        self.true_pixmap, self.false_pixmap = self.__ReadTrueAndFalesQPixmap()
        # 定义变量
        self.__DefinedVariable()

    def openCamera(self):
        """打开相机"""
        print("\t虚拟相机%d打开成功~" % self.cam_num)
        return 0

    def startGrabbing(self):
        """开始抓取"""
        self.is_run = True
        self.is_thread_open=True
        # 创建线程
        self.h_thread_handle = Thread(target=self.__WorkThread)
        self.h_thread_handle.setDaemon(True)
        self.h_thread_handle.start()
        # 记录状态
        self.is_thread_open = True

        print("虚拟相机%s开始抓取!" % self.cam_num)

    def stopGrabbing(self):
        """停止抓取"""
        # 若 抓取中 且 设备打开
        if self.is_thread_open:
            self.__StopThread(self.h_thread_handle)
            self.is_thread_open = False
            print("虚拟相机%s停止抓取成功!" % self.cam_num)

    def closeCamera(self):
        """关闭相机"""
        if self.is_thread_open:
            self.__StopThread(self.h_thread_handle)
            self.is_thread_open = False
            print("\t虚拟相机%s关闭成功~" % self.cam_num)

    def triggerOnce(self, serial_number):
        """触发一次"""
        # todo 未完成
        self.serial_number = serial_number

    def setParameter(self, frameRate, exposureTime, gain):
        pass

    def showBufferImage(self):
        numArray = self.cache_image_list[self.cam_num]
        if numArray is None:
            return

        self.__ProcessFlow(numArray)

    def __DefinedVariable(self):
        self.is_open = False
        self.is_run = False
        self.id = ''
        self.serial_number = ''
        self.sleep_time = 0.1

    def __WorkThread(self):
        """开启线程"""
        while True:
            self.image_id = f"{time.time():.0f}_{self.cam_num}_"
            self.count = 0
            for pic_path in self.image_path_list:
                if not self.is_run:
                    print(f'虚拟线程{self.cam_num}已终止~')
                    return
                numArray = cv2.imread(pic_path)
                # 图像处理流程
                self.__ProcessFlow(numArray)
                self.count += 1
                time.sleep(self.sleep_time)

    def __ShowImageToMainLabel(self, img: cv2):
        """向标签中显示彩图"""
        if len(img.shape) == 3:
            height, width, layer = img.shape
            qt_img_obj = QImage(img.data, width, height, width * layer, QImage.Format_BGR888)
        else:
            height, width = img.shape
            qt_img_obj = QImage(img.data, width, height, width, QImage.Format_Grayscale8)

        pixmap = QPixmap.fromImage(qt_img_obj).scaled(self.label_main_width, self.label_main_height)
        self.label_main.setPixmap(pixmap)

    def __ProcessFlow(self, numArray):
        """图像处理流程"""
        image_name = self.image_id + str(self.count)
        # 存入缓存列表
        self.cache_image_list[self.cam_num] = numArray
        # 1.图像处理,返回结果,BGR彩图,
        now_time = time.time()
        result, bgr, src = self.image_detect_class_obj.getProcessingResult(numArray)
        spent_time = time.time() - now_time
        # 2.向标签上显示图片
        if self.show_image_control_list[self.cam_num] == 0:
            pass
        elif self.show_image_control_list[self.cam_num] == 1:
            self.__ShowImageToMainLabel(bgr)
            # 向其它标签中显示信息
            self.__ShowInfoToOtherLabel(spent_time, self.__ErrorDict, result, image_name)
        elif self.show_image_control_list[self.cam_num] == 2:
            self.__ShowImageToMainLabel(src)
            # 向其它标签中显示信息
            self.__ShowInfoToOtherLabel(spent_time, self.__ErrorDict, result, image_name)
        # 若异常
        if result:
            # 存储结果
            self.all_camera_result_text_dict[f'camera{self.cam_num}'][
                self.serial_number] = f"{self.__ErrorDict(result)}_{self.cam_num}"
            if self.control_dict['ErrorStop']:
                # 触发回调, 出错暂停
                print(f'相机{self.cam_num}触发[出错暂停]')
                Thread(target=self.errorStop_CallbackFunction).start()
            # 保存异常图像
            self.__SaveExceptionImage(numArray, image_name + ".jpg")

    def __ShowInfoToOtherLabel(self, elapsed_time, errorDict, result, file_name):
        # 向判断标签中显示结果图片
        self.label_result.setPixmap(self.true_pixmap if not result else self.false_pixmap)
        # 向标签中显示时间
        self.label_info.setText(f"elapsed time:{elapsed_time * 1000:.0f} ms")
        # 显示剔除信息
        self.label_error.setText(f"{errorDict(result)}  {file_name}")

    def __ReadTrueAndFalesQPixmap(self):
        return (QPixmap('./File_Static/true.png').scaled(self.label_result.width(), self.label_result.height()),
                QPixmap('./File_Static/false.png').scaled(self.label_result.width(), self.label_result.height()))

    def __SaveExceptionImage(self, numArray, file_name):
        file_path = os.path.join(self.exception_path, file_name)
        cv2.imwrite(file_path, numArray)

    def __StopThread(self, thread):
        self.__Async_raise(thread.ident, SystemExit)

    def __ErrorDict(self, key):
        if key == 0:
            value = '正常'
        else:
            try:
                value = self.error_type_dict[key]
            except:
                value = '未知缺陷'
        return value

    @staticmethod
    def __Async_raise(tid, exctype):
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("无效的线程id!")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    @staticmethod
    def __TriggerRejector(serial_number: int):
        """触发剔除"""
        print(f'--> 触发剔除! 虚拟编号{serial_number} ...... <--')
