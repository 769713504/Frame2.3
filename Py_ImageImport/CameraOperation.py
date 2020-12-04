# -- coding: utf-8 --
import ctypes
import datetime
import inspect
import os
import time
from threading import Thread

import cv2
import numpy as np
from PyQt5.QtGui import QPixmap, QImage

from Py_ImageImport.CameraParams_header import *
from Py_ImageImport.MvCameraControl_class import *
from Py_ImageImport.PixelType_header import *


class CameraOperation:
    """相机操作类"""

    def __init__(self,
                 st_device_list,  # 设备信息列表
                 cam_num,  # 当前相机编号
                 label_obj_dict,  # 标签对象字典
                 show_image_control_list,  # 显示图的控制列表
                 visual_detection_class_obj,  # 图像检测类
                 exception_path,  # 异常图片目录
                 cache_image_list,  # 缓存图像列表
                 control_dict,  # 控制字典
                 save_image_mode_dict,  # 保存图像模式的字典
                 save_path,  # 保存图像的路径
                 all_camera_result_text_dict,  # 缓存结果的字典
                 errorStop_CallbackFunction,  # 回调函数:出错暂停
                 triggerRejector_CallbackFunction  # 触发剔除
                 ):
        self.st_device_list = st_device_list
        self.cam_num = cam_num

        # 标签对象
        self.label_main = label_obj_dict['label_main']
        self.label_error = label_obj_dict['label_error']
        self.label_info = label_obj_dict['label_info']
        self.label_result = label_obj_dict['label_result']

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

        # 保存图像目录的路径
        self.save_image_dir_path = self.__GetSaveImageDirPath(save_path)
        # 当前相机缓存结果的字典
        self.all_camera_result_text_dict = all_camera_result_text_dict
        # 触发剔除的函数
        self.triggerRejector_CallbackFunction = triggerRejector_CallbackFunction
        # 定义变量
        self.__DefinedVariable()

    def openCamera(self):
        """打开相机"""
        # todo 未完成
        st_device_list = cast(self.st_device_list.pDeviceInfo[self.cam_num], POINTER(MV_CC_DEVICE_INFO)).contents
        # 给相机对象创建句柄
        if self.camera_obj.MV_CC_CreateHandle(st_device_list):
            # 销毁句柄
            self.camera_obj.MV_CC_DestroyHandle()
            print('错误!', '相机{}创建句柄失败!')
            return -1
        # 打开设备
        elif self.camera_obj.MV_CC_OpenDevice(MV_ACCESS_Exclusive):
            print("\t相机%d打开失败!" % self.cam_num)
            return -2
        else:
            print("\t相机%d打开成功~" % self.cam_num)

        # 探测GigE网络最佳包大小
        if st_device_list.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = self.camera_obj.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = self.camera_obj.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                if ret != 0:
                    print("警告: 设置数据包大小失败! ret[0x%x]" % ret)
            else:
                print("警告: 设置数据包大小失败! ret[0x%x]" % nPacketSize)

        stBool = c_bool(False)
        ret = self.camera_obj.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", byref(stBool))
        if ret != 0:
            print("[获取帧率]开启失败! ret[0x%x]" % ret)

        stParam = MVCC_INTVALUE()
        memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))

        ret = self.camera_obj.MV_CC_GetIntValue("PayloadSize", stParam)  # 有效负载大小
        if ret != 0:
            print("获取[有效负载大小]失败! ret[0x%x]" % ret)
        self.n_payload_size = stParam.nCurValue

        if not self.buf_cache:  # 如果缓存区域为空 设置缓存区域
            self.buf_cache = (c_ubyte * self.n_payload_size)()

        # 设置触发模式为软触发
        if self.camera_obj.MV_CC_SetEnumValue("TriggerMode", 1):
            print('错误!', '设置触发模式失败!')
            return -4
        elif self.camera_obj.MV_CC_SetEnumValue("TriggerSource", 7):
            print('错误!', '设置触发模式失败!')
            return -5
        else:
            return 0

    def startGrabbing(self):
        """开始抓取"""

        if self.camera_obj.MV_CC_StartGrabbing():
            # return print( '错误!', '开始抓取失败!')
            return print('相机%d开始抓取失败!' % self.cam_num)

        else:
            # 创建线程
            self.h_thread_handle = Thread(target=self.__WorkThread)
            self.h_thread_handle.setDaemon(True)
            self.h_thread_handle.start()
            # 记录状态
            self.is_thread_open = True

            print("相机%s开始抓取!" % self.cam_num)

    def stopGrabbing(self):
        """停止抓取"""

        # 若 抓取中 且 设备打开
        if self.is_thread_open:
            self.__StopThread(self.h_thread_handle)
            self.is_thread_open = False

        if self.camera_obj.MV_CC_StopGrabbing():
            print('错误!', '停止抓取失败!')
            return -1
        else:
            print("相机%s停止抓取成功!" % self.cam_num)
            return 0

    def closeCamera(self):
        """关闭相机"""

        if self.is_thread_open:
            self.__StopThread(self.h_thread_handle)
            self.is_thread_open = False
        if self.camera_obj.MV_CC_CloseDevice():
            print('错误!', '关闭设备失败!')
            return -1
        else:
            # 销毁句柄
            self.camera_obj.MV_CC_DestroyHandle()
            print("\t相机%s关闭成功~" % self.cam_num)
            return 0

    def triggerOnce(self, serial_number):
        """触发一次"""
        self.serial_number = serial_number
        if self.camera_obj.MV_CC_SetCommandValue("TriggerSoftware"):
            print('错误!', '软触发失败!')

    def setParameter(self, frameRate, exposureTime, gain):
        """设置参数"""

        if self.camera_obj.MV_CC_SetFloatValue("ExposureTime", float(exposureTime)):
            print('错误!', '设置曝光时间失败!', exposureTime)
        elif self.camera_obj.MV_CC_SetFloatValue("Gain", float(gain)):
            print('错误!', '增益设置失败!', gain)
        elif self.camera_obj.MV_CC_SetFloatValue("AcquisitionFrameRate", float(frameRate)):
            print('错误!', '设置获取帧速率失败!', frameRate)
        else:
            print(f'相机{self.cam_num}参数设置成功~')

    def __DefinedVariable(self):
        # 声明变量
        self.is_save_bmp = None
        self.is_save_jpg = None
        self.is_exit = None  # 是否退出
        self.is_grabbing = None  # 是否抓取
        self.is_thread_open = None
        self.st_frame_info = None  # 帧信息
        self.buf_cache = None  # 缓存区大小
        self.n_payload_size = None  # 有效负荷大小
        self.buf_save_image = None  # 在缓存区保存的图像
        self.h_thread_handle = None  # 线程句柄
        self.save_image_size = None  # 保存图像的大小
        # 参数设置
        self.frame_rate = 0
        self.exposure_time = 0
        self.gain = 0
        # 获取相机对象
        self.camera_obj = MvCamera()
        # 窗口宽高
        self.label_main_width, self.label_main_height = self.label_main.width(), self.label_main.height()
        # 读取对错图对象
        self.true_pixmap, self.false_pixmap = self.__ReadTrueAndFalesQPixmap()

    def __GetSaveImageDirPath(self, save_path):
        """获取保存图片的文件夹路径"""
        # todo 未完成
        save_image_dir_path = os.path.join(save_path, f'camera{self.cam_num}')
        if not os.path.exists(save_image_dir_path):
            os.mkdir(save_image_dir_path)
        return save_image_dir_path

    def __SaveImage(self):
        if self.save_image_mode_dict['save_type']:
            self.__SaveBmp()
        else:
            self.__SaveJpg()

    def __ShowInfoToOtherLabel(self, spent, result, file_name):
        # 向判断标签中显示结果图片
        self.label_result.setPixmap(self.true_pixmap if not result else self.false_pixmap)
        # 向标签中显示时间
        self.label_info.setText(f"elapsed time:{spent * 1000:.0f} ms")
        # 显示剔除信息
        self.label_error.setText(f"{self.__ErrorDict(result)}  {file_name}")

    def __WorkThread(self):
        """开启线程"""
        stFrameInfo = MV_FRAME_OUT_INFO_EX()  # 图像信息结构体 : 包含宽高 曝光增益 ...
        img_buff = None  # 图像缓存
        self.id = str(self.cam_num) + '_' + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '_')
        while True:
            #                                           (图像数据接收指针[OUT],接收缓存大小[IN],图像信息结构体[OUT],等待超时时间[IN])
            ret = self.camera_obj.MV_CC_GetOneFrameTimeout(byref(self.buf_cache), self.n_payload_size, stFrameInfo,
                                                           1000)
            if ret == 0:
                # 获取到图像的时间开始节点获取到图像的时间开始节点
                self.st_frame_info = stFrameInfo
                print("相机%s:第%d帧: %d X %d Px" % (self.cam_num,
                                                 self.st_frame_info.nFrameNum,
                                                 self.st_frame_info.nWidth,
                                                 self.st_frame_info.nHeight))
                self.save_image_size = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3 + 2048
                if img_buff is None:
                    img_buff = (c_ubyte * self.save_image_size)()

                if not self.buf_save_image:
                    self.buf_save_image = (c_ubyte * self.save_image_size)()

                if self.is_save_jpg:
                    self.__SaveJpg()  # 保存Jpg图片
                if self.is_save_bmp:
                    self.__SaveBmp()  # 保存Bmp图片
            else:
                continue

            # 转换像素结构体赋值
            stConvertParam = MV_CC_PIXEL_CONVERT_PARAM()
            memset(byref(stConvertParam), 0, sizeof(stConvertParam))
            stConvertParam.nWidth = self.st_frame_info.nWidth
            stConvertParam.nHeight = self.st_frame_info.nHeight
            stConvertParam.pSrcData = self.buf_cache
            stConvertParam.nSrcDataLen = self.st_frame_info.nFrameLen
            stConvertParam.enSrcPixelType = self.st_frame_info.enPixelType

            # 定义ndarray类型的numArray
            numArray = np.array([])
            # 处理拜耳RG8彩图
            if PixelType_Gvsp_BayerRG8 == self.st_frame_info.enPixelType:
                nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
                stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize

                ret = self.camera_obj.MV_CC_ConvertPixelType(stConvertParam)
                if ret != 0:
                    print('错误!', '像素转换失败! ret = {}'.format(self.__ToHexStr(ret)))
                    continue
                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                numArray = self.__ColorNumpy(img_buff, self.st_frame_info.nWidth, self.st_frame_info.nHeight)
            # Mono8直接显示
            elif PixelType_Gvsp_Mono8 == self.st_frame_info.enPixelType:
                numArray = self.__MonoNumpy(self.buf_cache, self.st_frame_info.nWidth,
                                            self.st_frame_info.nHeight)
            # RGB直接显示
            elif PixelType_Gvsp_RGB8_Packed == self.st_frame_info.enPixelType:
                numArray = self.__ColorNumpy(self.buf_cache, self.st_frame_info.nWidth,
                                             self.st_frame_info.nHeight)
            # 如果是黑白且非Mono8则转为Mono8
            elif self.__IsMonoData(self.st_frame_info.enPixelType):
                nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight
                stConvertParam.enDstPixelType = PixelType_Gvsp_Mono8
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize
                ret = self.camera_obj.MV_CC_ConvertPixelType(stConvertParam)
                if ret != 0:
                    print('错误!', '像素转换失败! ret = {}'.format(self.__ToHexStr(ret)))
                    continue
                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                numArray = self.__MonoNumpy(img_buff, self.st_frame_info.nWidth,
                                            self.st_frame_info.nHeight)
            # 如果是彩色且非RGB则转为RGB后显示
            elif self.__IsColorData(self.st_frame_info.enPixelType):
                nConvertSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight * 3
                stConvertParam.enDstPixelType = PixelType_Gvsp_RGB8_Packed
                stConvertParam.pDstBuffer = (c_ubyte * nConvertSize)()
                stConvertParam.nDstBufferSize = nConvertSize

                ret = self.camera_obj.MV_CC_ConvertPixelType(stConvertParam)
                if ret != 0:
                    print('错误!', '像素转换失败! ret = {}'.format(self.__ToHexStr(ret)))
                    continue
                cdll.msvcrt.memcpy(byref(img_buff), stConvertParam.pDstBuffer, nConvertSize)
                numArray = self.__ColorNumpy(img_buff, self.st_frame_info.nWidth, self.st_frame_info.nHeight)

            # 图像处理流程
            self.__ProcessFlow(numArray)

    def showBufferImage(self):
        numArray = self.cache_image_list[self.cam_num]
        if numArray is None:
            return
        self.__ProcessFlow(numArray)

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
        # 存入缓存列表
        self.cache_image_list[self.cam_num] = numArray
        # 拼接文件名
        file_name = self.id + str(self.st_frame_info.nFrameNum)

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
            self.__ShowInfoToOtherLabel(spent_time, result, file_name)
        elif self.show_image_control_list[self.cam_num] == 2:
            self.__ShowImageToMainLabel(src)
            # 向其它标签中显示信息
            self.__ShowInfoToOtherLabel(spent_time, result, file_name)

        # 若异常
        if result:
            # 存储结果
            self.all_camera_result_text_dict[f'camera{self.cam_num}'][
                self.serial_number] = f"{self.__ErrorDict(result)}_{self.cam_num}"

            if self.control_dict['Rejector']:
                # 判断剔除是否开启, 触发剔除
                self.triggerRejector_CallbackFunction(self.serial_number)
            if self.control_dict['ErrorStop']:
                # 触发回调, 出错暂停
                print(f'相机{self.cam_num}触发[出错暂停]')
                Thread(target=self.errorStop_CallbackFunction).start()

            # 保存异常图像
            self.__SaveExceptionImage(file_name + ".bmp")

        # 判断保存图像模式
        if self.save_image_mode_dict['save_mode']:
            if self.save_image_mode_dict['save_mode'] == 3:
                if result:
                    self.__SaveImage()
            elif self.save_image_mode_dict['save_mode'] == 2:
                if not result:
                    self.__SaveImage()
            elif self.save_image_mode_dict['save_mode'] == 1:
                self.__SaveImage()

    def __ReadTrueAndFalesQPixmap(self):
        return QPixmap('./File_Static/true.png').scaled(self.label_result.width(), self.label_result.height()), \
               QPixmap('./File_Static/false.png').scaled(self.label_result.width(), self.label_result.height())

    def __StopThread(self, thread):
        self.__Async_raise(thread.ident, SystemExit)

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
    def __ToHexStr(num):
        """转换十六进制"""
        chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
        hexStr = ""
        if num < 0:
            num = num + 2 ** 32
        while num >= 16:
            digit = num % 16
            hexStr = chaDic.get(digit, str(digit)) + hexStr
            num //= 16
        hexStr = chaDic.get(num, str(num)) + hexStr
        return hexStr

    @staticmethod
    def __IsColorData(enGvspPixelType):
        """判断彩图"""
        if PixelType_Gvsp_BayerGR8 == enGvspPixelType \
                or PixelType_Gvsp_BayerRG8 == enGvspPixelType \
                or PixelType_Gvsp_BayerGB8 == enGvspPixelType \
                or PixelType_Gvsp_BayerBG8 == enGvspPixelType \
                or PixelType_Gvsp_BayerGR10 == enGvspPixelType \
                or PixelType_Gvsp_BayerRG10 == enGvspPixelType \
                or PixelType_Gvsp_BayerGB10 == enGvspPixelType \
                or PixelType_Gvsp_BayerBG10 == enGvspPixelType \
                or PixelType_Gvsp_BayerGR12 == enGvspPixelType \
                or PixelType_Gvsp_BayerRG12 == enGvspPixelType \
                or PixelType_Gvsp_BayerGB12 == enGvspPixelType \
                or PixelType_Gvsp_BayerBG12 == enGvspPixelType \
                or PixelType_Gvsp_BayerGR10_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerRG10_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerGB10_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerBG10_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerGR12_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerRG12_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerGB12_Packed == enGvspPixelType \
                or PixelType_Gvsp_BayerBG12_Packed == enGvspPixelType \
                or PixelType_Gvsp_YUV422_Packed == enGvspPixelType \
                or PixelType_Gvsp_YUV422_YUYV_Packed == enGvspPixelType:
            return True
        else:
            return False

    @staticmethod
    def __MonoNumpy(data, nWidth, nHeight):
        """Mono转numpy"""
        data_ = np.frombuffer(data, count=int(nWidth * nHeight), dtype=np.uint8, offset=0)
        data_mono_arr = data_.reshape(nHeight, nWidth)
        numArray = np.zeros([nHeight, nWidth, 1], "uint8")
        numArray[:, :, 0] = data_mono_arr
        return numArray

    @staticmethod
    def __ColorNumpy(data, nWidth, nHeight):
        """Color转numpy"""
        data_ = np.frombuffer(data, count=int(nWidth * nHeight * 3), dtype=np.uint8, offset=0)
        data_r = data_[0:nWidth * nHeight * 3:3]
        data_g = data_[1:nWidth * nHeight * 3:3]
        data_b = data_[2:nWidth * nHeight * 3:3]

        data_r_arr = data_r.reshape(nHeight, nWidth)
        data_g_arr = data_g.reshape(nHeight, nWidth)
        data_b_arr = data_b.reshape(nHeight, nWidth)
        numArray = np.zeros([nHeight, nWidth, 3], "uint8")

        numArray[:, :, 2] = data_r_arr
        numArray[:, :, 1] = data_g_arr
        numArray[:, :, 0] = data_b_arr
        return numArray

    @staticmethod
    def __IsMonoData(enGvspPixelType):
        """判断灰度图"""
        if PixelType_Gvsp_Mono8 == enGvspPixelType or PixelType_Gvsp_Mono10 == enGvspPixelType \
                or PixelType_Gvsp_Mono10_Packed == enGvspPixelType or PixelType_Gvsp_Mono12 == enGvspPixelType \
                or PixelType_Gvsp_Mono12_Packed == enGvspPixelType:
            return True
        else:
            return False

    def __SaveJpg(self):
        """保存图片"""
        file_path = os.path.join(self.save_image_dir_path, self.id + f'{self.st_frame_info.nFrameNum}.jpg')

        stParam = MV_SAVE_IMAGE_PARAM_EX()
        stParam.enImageType = MV_Image_Jpeg  # 需要保存的图像类型
        stParam.enPixelType = self.st_frame_info.enPixelType  # 相机对应的像素格式
        stParam.nWidth = self.st_frame_info.nWidth  # 相机对应的宽
        stParam.nHeight = self.st_frame_info.nHeight  # 相机对应的高
        stParam.nDataLen = self.st_frame_info.nFrameLen
        stParam.pData = cast(self.buf_cache, POINTER(c_ubyte))
        stParam.pImageBuffer = cast(byref(self.buf_save_image), POINTER(c_ubyte))
        stParam.nBufferSize = self.save_image_size  # 存储节点的大小
        stParam.nJpgQuality = 80  # jpg编码，仅在保存Jpg图像时有效。保存BMP时SDK内忽略该参数
        return_code = self.camera_obj.MV_CC_SaveImageEx2(stParam)

        if return_code:
            print('保存jpg失败!')
        else:
            img_buff = (c_ubyte * stParam.nImageLen)()
            cdll.msvcrt.memcpy(byref(img_buff), stParam.pImageBuffer, stParam.nImageLen)

            with open(file_path.encode('ascii'), 'wb+') as f:
                f.write(img_buff)

    def __SaveBmp(self):
        """保存图片"""
        file_path = os.path.join(self.save_image_dir_path, self.id + f'{self.st_frame_info.nFrameNum}.bmp')

        stParam = MV_SAVE_IMAGE_PARAM_EX()
        stParam.enImageType = MV_Image_Bmp  # 需要保存的图像类型
        stParam.enPixelType = self.st_frame_info.enPixelType  # 相机对应的像素格式
        stParam.nWidth = self.st_frame_info.nWidth  # 相机对应的宽
        stParam.nHeight = self.st_frame_info.nHeight  # 相机对应的高
        stParam.nDataLen = self.st_frame_info.nFrameLen
        stParam.pData = cast(self.buf_cache, POINTER(c_ubyte))
        stParam.pImageBuffer = (c_ubyte * self.save_image_size)()
        stParam.nBufferSize = self.save_image_size  # 存储节点的大小
        return_code = self.camera_obj.MV_CC_SaveImageEx2(stParam)

        if return_code:
            print('保存bmp失败!')
        else:
            img_buff = (c_ubyte * stParam.nImageLen)()
            cdll.msvcrt.memcpy(byref(img_buff), stParam.pImageBuffer, stParam.nImageLen)
            with open(file_path.encode('ascii'), 'wb+') as f:
                f.write(img_buff)

    def __SaveExceptionImage(self, file_name):
        """保存异常图片"""
        file_path = os.path.join(self.exception_path, file_name)

        stParam = MV_SAVE_IMAGE_PARAM_EX()
        stParam.enImageType = MV_Image_Bmp  # 需要保存的图像类型
        stParam.enPixelType = self.st_frame_info.enPixelType  # 相机对应的像素格式
        stParam.nWidth = self.st_frame_info.nWidth  # 相机对应的宽
        stParam.nHeight = self.st_frame_info.nHeight  # 相机对应的高
        stParam.nDataLen = self.st_frame_info.nFrameLen
        stParam.pData = cast(self.buf_cache, POINTER(c_ubyte))
        stParam.pImageBuffer = (c_ubyte * self.save_image_size)()
        stParam.nBufferSize = self.save_image_size  # 存储节点的大小
        return_code = self.camera_obj.MV_CC_SaveImageEx2(stParam)
        if return_code:
            return -1
        else:
            img_buff = (c_ubyte * stParam.nImageLen)()
            print(img_buff)
            cdll.msvcrt.memcpy(byref(img_buff), stParam.pImageBuffer, stParam.nImageLen)
            with open(file_path.encode('ascii'), 'wb+') as f:
                f.write(img_buff)

    def __ErrorDict(self, key):
        if key == 0:
            value = '正常'
        else:
            try:
                value = self.error_type_dict[key]
            except:
                value = '未知缺陷'
        return value
