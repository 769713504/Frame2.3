def startRun(self):
    """开始运行"""

    # 根据 运行模式 选择

    # 传感器触发
    if self.run_mode == 0:
        self.startEncoderTrigger()
    # 时间触发
    elif self.run_mode == 1:
        # 循环开启取流
        self.cycleStartGrabbing()
    # 模拟触发
    elif self.run_mode == 2:
        # 循环模拟取流
        self.cycleSimulateGrabbing()


def stopRun(self):
    """停止运行"""
    # 根据 运行模式 选择

    # 传感器触发
    if self.run_mode == 0:
        self.stopEncoderTrigger()
    # 时间触发
    elif self.run_mode == 1:
        # 循环停止取流
        self.cycleStopGrabbing()
    # 模拟触发
    elif self.run_mode == 2:
        pass

    self.updateCsv()
    print('--> 保存CSV完成 <--')


def Get_parameter(self):
    """获取参数"""
    if self.is_camera_open:
        stFloatParam_FrameRate = MVCC_FLOATVALUE()
        memset(byref(stFloatParam_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
        stFloatParam_exposureTime = MVCC_FLOATVALUE()
        memset(byref(stFloatParam_exposureTime), 0, sizeof(MVCC_FLOATVALUE))
        stFloatParam_gain = MVCC_FLOATVALUE()
        memset(byref(stFloatParam_gain), 0, sizeof(MVCC_FLOATVALUE))
        ret = self.camera_obj.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatParam_FrameRate)
        if ret != 0:
            QMessageBox(QMessageBox.Critical, '错误!', '获取帧率失败! ret = {}'.format(self.__ToHexStr(ret))).exec_()
        self.frame_rate = stFloatParam_FrameRate.fCurValue
        ret = self.camera_obj.MV_CC_GetFloatValue("ExposureTime", stFloatParam_exposureTime)
        if ret != 0:
            QMessageBox(QMessageBox.Critical, '错误!', '获取曝光时间失败! ret = {}'.format(self.__ToHexStr(ret))).exec_()
        self.exposure_time = stFloatParam_exposureTime.fCurValue
        ret = self.camera_obj.MV_CC_GetFloatValue("Gain", stFloatParam_gain)
        if ret != 0:
            QMessageBox(QMessageBox.Critical, '错误!', '获取增益失败! ret = {}'.format(self.__ToHexStr(ret))).exec_()
        self.gain = stFloatParam_gain.fCurValue
        QMessageBox(QMessageBox.Critical, '错误!', '获取参数成功! ret = {}'.format(self.__ToHexStr(ret))).exec_()


def simulateGrabbing(self, cam_num):
    """模拟抓取"""

    def __ErrorDict(key: int) -> str:
        """局部函数"""
        if key == 0:
            value = '正常'
        else:
            try:
                value = error_type_dict[key]
            except:
                value = '未知缺陷'
        return value

    # 视觉检测类对象
    image_detect_obj = self.visual_detection_obj_list[cam_num]
    # 休眠时间
    sleep_time = self.sleep_time_list[cam_num]
    # 图片路径列表
    image_path_list = self.all_camera_image_path_list_list[cam_num]
    # 缺陷字典
    error_type_dict = image_detect_obj.defErrorType()
    # 相机图片编号
    cam_id = f'{cam_num}_' + self.id
    # 编号
    n = 0
    print(f'虚拟线程{cam_num}已启动~')
    while True:
        for pic_path in image_path_list:
            n += 1
            if not self.is_run:
                print(f'虚拟线程{cam_num}已终止~')
                return
            numArray = cv2.imread(pic_path)
            file_name = cam_id + f'_{n}'

            print(f'虚拟相机{cam_num}: 图像{n}:{file_name}')
            self.cache_image_list[cam_num] = numArray
            # 1.图像处理,返回结果,BGR彩图,
            now_time = time.time()
            result, img, src = image_detect_obj.getProcessingResult(numArray)
            spent_time = time.time() - now_time
            # 2.向标签上显示图片
            if self.show_image_control_list[cam_num] == 0:
                pass
            elif self.show_image_control_list[cam_num] == 1:
                self.__ShowThreeChannelImage(img)
                # 向其它标签中显示信息
                self.__ShowInfoToOtherLabel(spent_time, __ErrorDict, result, file_name)
            elif self.show_image_control_list[cam_num] == 2:
                if len(src.shape) == 2:
                    self.__ShowSingleChannelImage(src)
                else:
                    self.__ShowThreeChannelImage(src)
                # 向其它标签中显示信息
                self.__ShowInfoToOtherLabel(spent_time, __ErrorDict, result, file_name)

            # 结果处理
            if result:
                if self.control_dict['Rejector']:
                    # 判断剔除是否开启, 触发剔除
                    self.sensor_control_obj.triggerRejector_CallbackFunction(n)
                if self.control_dict['ErrorStop']:
                    # 触发回调, 出错暂停
                    print(f'-->相机{cam_num}触发[出错暂停]<--')
                    Thread(target=self.errorStop_CallbackFunction).start()
                # 保存异常图像
                self.__SaveBmpToExceptionDirectory(numArray, file_name + ".bmp")

            time.sleep(sleep_time)


def initCameraParam(self):
    """初始化相机参数"""
    for i in range(self.cam_sum):
        camera_ini_obj = self.camera_config_obj_list[i]
        if self.run_mode == 0 or self.run_mode == 1:
            camera_obj = self.camera_operation_obj_list[i]
            camera_obj.setParameter(frameRate=camera_ini_obj['camera']['framerate'],
                                    exposureTime=camera_ini_obj['camera']['exposuretime'],
                                    gain=camera_ini_obj['camera']['gain'])
            print('相机%s读参成功~' % i)

def xFunc(self):
    """绑定下拉列表至设备信息索引"""
    # noinspection PyGlobalUndefined
    global nSelCamIndex
    nSelCamIndex = self.TxtWrapBy("[", "]", self.device_list.get())
