# -- coding: utf-8 --
# 应用主程序
import configparser
import shutil
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QLineEdit, QMessageBox

from Py_Main.CameraOperation import *
from Py_Main.SimulationOperation import SimulationOperation
from Py_Main.MainWindow import Ui_MainWindow
from Py_Main.SensorControl import SensorSerialPortControl


class Main(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 设置系统配置路径
        self.config_path = './File_Config'
        # 读取系统参数
        self.getSystemParameter()
        # 读取相机配置
        self.getCameraConfigInfo()
        # 初始化变量
        self.defineVariable()
        # 从方法初始化变量
        self.initializeVariable()
        # 初始化设置
        self.initializeSetting()

        # 单选按钮
        self.radioButton_0.clicked.connect(lambda: self.changNowCamera(0))
        self.radioButton_1.clicked.connect(lambda: self.changNowCamera(1))
        self.radioButton_2.clicked.connect(lambda: self.changNowCamera(2))
        self.radioButton_3.clicked.connect(lambda: self.changNowCamera(3))
        self.radioButton_4.clicked.connect(lambda: self.changNowCamera(4))
        self.radioButton_5.clicked.connect(lambda: self.changNowCamera(5))
        # 复选按钮
        self.checkBox.clicked.connect(self.selectSimulateRun)  # 模拟运行
        # 普通按钮
        self.pushButton_00.clicked.connect(self.restartDevice)  # 重启设备
        self.pushButton_01.clicked.connect(self.showImageToMainLabelByPushButtonControl)  # 原始图像/灰度图
        self.pushButton_02.clicked.connect(self.Window_CameraConfig)  # ---->相机配置
        self.pushButton_03.clicked.connect(self.Window_ExceptionImage)  # 异常图像
        self.pushButton_04.clicked.connect(self.errorStop)  # 出错暂停
        self.pushButton_05.clicked.connect(self.startOrStopRun)  # 启动/停止运行
        self.pushButton_06.clicked.connect(self.trainingMode)  # 训练模式/保存训练
        self.pushButton_07.clicked.connect(self.rejectorSwitch)  # 剔除开关
        self.pushButton_08.clicked.connect(self.monitorSwitch)  # 监视状态
        self.pushButton_09.clicked.connect(self.Window_ChangeProduct)  # ---->产品选择
        self.pushButton_10.clicked.connect(self.closeDevice)  # 退出:关闭设备
        self.pushButton_11.clicked.connect(self.changeShift)  # 换班
        # 菜单按钮
        self.action_01.triggered.connect(self.Window_SystemConfig)  # ---->系统配置
        self.action_02.triggered.connect(self.Window_SaveMode)  # ---->保存模式

    def setAllCameraParam(self):
        """设置所有相机参数"""
        for i in range(self.cam_sum):
            camera_config_obj = self.camera_config_obj_list[i]
            camera_operation_obj = self.camera_operation_obj_list[i]
            camera_operation_obj.setParameter(frameRate=camera_config_obj['camera']['framerate'],
                                              exposureTime=camera_config_obj['camera']['exposuretime'],
                                              gain=camera_config_obj['camera']['gain'])

    def displayFromCache(self):
        """从缓存显示"""
        if self.is_run:
            # 若运行中则不执行
            return
        self.camera_operation_obj_list[self.now_show_num].showBufferImage()

    def defineVariable(self):
        """定义变量: 在此处实现,无需调用方法"""

        # 定义计数
        self.count = 0
        # 当前显示编号: 显示n相机的 参数 与 采图
        self.now_show_num = 0
        # 触发计数
        self.trigger_count = 0
        # 所有编号统计
        self.all_number_dict = {}
        # 相机打开状态
        self.is_open = False
        # 相机运行状态
        self.is_run = False
        # # 线程列表
        # self.thread_list = []
        # 线程向label_main传图的控制列表:1原图 2灰度图 False关闭
        self.show_image_control_list = [1, False, False, False, False, False]
        # 缓存图像列表
        self.cache_image_list = [None, None, None, None, None, None]
        # 控制字典  {'Rejector': 剔除器, 'ErrorStop': 出错暂停, 'SeveMode': 保存图片模式}
        self.control_dict = {'Rejector': False, 'ErrorStop': False, 'SeveMode': 0}
        # 保存图像模式字典 Jpg/Png, 全保存/仅正确/仅错误/不保存
        self.save_image_mode_dict = {'save_mode': self.save_mode, 'save_type': self.save_type}
        # 所有相机缓存结果字典
        self.all_camera_result_text_dict = {f'camera{i}': {} for i in range(self.cam_sum)}
        # 标签对象字典
        self.label_obj_dict = {'label_main': self.label_main, 'label_info': self.label_info,
                               'label_result': self.label_result, 'label_error': self.label_error}
        self.sleep_time = 0.1

    def initializeVariable(self):
        """初始化变量"""

        # 异常图像存储路径
        self.exception_path = self.createExceptionDirectory()
        # 传感器控制类对象
        self.sensor_control_obj = SensorSerialPortControl(self.control_port)
        # 视觉检测对象列表
        self.visual_detection_obj_list = self.getVisualDetectionClassObjList(self.cam_sum)

        # 获取 参数列表对象 列表
        self.args_list_obj_list = self.getArgsListObjList()
        # 初始化参数列表: 向参数列表中添加参数
        self.all_spinBox_list_dic = self.createArgsListDict()
        # 窗口宽高
        self.label_main_width, self.label_main_height = self.label_main.width(), self.label_main.height()

        # 所有相机配置文件中的坐标列表
        self.train_coordinates_list = self.getTrainCoordinatesList()
        # 所有相机配置文件中 图像缩放比列表[[1.6,1.6],[x,y],...]
        self.train_zoom_ratio_list = self.getZoomRatioList()
        # 初始化日表对象
        self.csv_path = self.getCsvPath()
        # "批"时间ID
        self.batch_time_number = self.getTimeNumber()
        # 相机操作对象列表(含虚拟)
        self.camera_operation_obj_list = self.getOperationObjList()

    def getOperationObjList(self):
        """初始化相机操作类列表: 返回图像检测类的对象列表"""
        if self.run_mode == 2:
            all_camera_image_path_list_list = self.getAllCameraImagePathListList()
            return [SimulationOperation(
                cam_num=cam_num,  # 相机编号
                label_obj_dict=self.label_obj_dict,  # 标签对象字典
                image_path_list=all_camera_image_path_list_list[cam_num],  # 图片路径列表
                show_image_control_list=self.show_image_control_list,
                visual_detection_class_obj=self.visual_detection_obj_list[cam_num],
                exception_path=self.exception_path,
                cache_image_list=self.cache_image_list,
                control_dict=self.control_dict,
                errorStop_CallbackFunction=self.errorStop_CallbackFunction,
                save_image_mode_dict=self.save_image_mode_dict,
                all_camera_result_text_dict=self.all_camera_result_text_dict)
                for cam_num in range(self.cam_sum)]
        else:
            # 相机操作对象列表:存储实例化的相机操作对象
            if self.run_mode == 1:
                self.sensor_control_obj.sleep_time = self.sleep_time
                rejectorFunction = self.sensor_control_obj.timeSimulationRejector
                self.trigger_CallbackFunction = self.allCameraTriggerOnce
                self.signal_CallbackFunction = self.sensor_control_obj.getTimeSignal
            else:
                rejectorFunction = self.sensor_control_obj.triggerSensorRejector
                self.trigger_CallbackFunction = self.piecewiseTriggerOnce
                self.signal_CallbackFunction = self.sensor_control_obj.getSensorSignal

            return [CameraOperation(
                st_device_list=self.device_info,
                cam_num=cam_num,  # 相机编号
                label_obj_dict=self.label_obj_dict,  # 标签对象字典
                show_image_control_list=self.show_image_control_list,
                visual_detection_class_obj=self.visual_detection_obj_list[cam_num],
                exception_path=self.exception_path,
                cache_image_list=self.cache_image_list,
                control_dict=self.control_dict,
                errorStop_CallbackFunction=self.errorStop_CallbackFunction,
                save_path=self.save_path,
                save_image_mode_dict=self.save_image_mode_dict,
                all_camera_result_text_dict=self.all_camera_result_text_dict,
                triggerRejector_CallbackFunction=rejectorFunction)
                for cam_num in range(self.cam_sum)]

    def initializeSetting(self):
        """初始化设置"""

        # 隐藏多余的单选按钮
        self.hideRadioButton(self.cam_sum)

        # 更改产品标签
        self.label_product.setText(self.product_type)
        # 禁用参数列表
        self.monitorSwitch()
        # 初始化单选按钮
        self.changNowCamera(0)
        # 初始化所有相机坐标
        self.updateAllCoordinates()
        # 启动更新csv线程
        self.startUpdataCsv()
        # 设置剔除按钮
        self.setRejectorButton()
        # 打开相机
        self.openAllCamera()
        # 读取参数
        self.setAllCameraParam()

    # noinspection PyUnresolvedReferences,PyBroadException
    @staticmethod
    def getVisualDetectionClassObjList(cam_sum):
        """初始化图像检测类:将实例化的检测类对象保存到 self.visual_detection_obj_list 中"""
        from Py_CV.default import VisualDetection as VI

        image_detect_obj_list = []
        if cam_sum > 0:
            try:
                from Py_CV.camera0 import VisualDetection
                image_detect_obj_list.append(VisualDetection(0))
            except Exception:
                image_detect_obj_list.append(VI(0))
        if cam_sum > 1:
            try:
                from Py_CV.camera1 import VisualDetection
                image_detect_obj_list.append(VisualDetection(1))
            except Exception:
                image_detect_obj_list.append(VI(1))
        if cam_sum > 2:
            try:
                from Py_CV.camera2 import VisualDetection
                image_detect_obj_list.append(VisualDetection(2))
            except Exception:
                image_detect_obj_list.append(VI(2))
        if cam_sum > 3:
            try:
                from Py_CV.camera3 import VisualDetection
                image_detect_obj_list.append(VisualDetection(3))
            except Exception:
                image_detect_obj_list.append(VI(3))
        if cam_sum > 4:
            try:
                from Py_CV.camera4 import VisualDetection
                image_detect_obj_list.append(VisualDetection(4))
            except Exception:
                image_detect_obj_list.append(VI(4))
        if cam_sum > 5:
            try:
                from Py_CV.camera5 import VisualDetection
                image_detect_obj_list.append(VisualDetection(5))
            except Exception:
                image_detect_obj_list.append(VI(5))
        return image_detect_obj_list

    def getCameraConfigInfo(self):
        """获取相机配置"""
        self.cam_sum = self.getCameraSum()
        # 读取相机配置
        self.camera_config_path_list = self.getConfigPathList()
        self.camera_config_obj_list = self.getConfigObjList(self.camera_config_path_list)

    def getCameraSum(self):
        # 获取设备信息 和 相机数量
        if self.run_mode == 2:
            cam_sum = self.save_type = self.system_config_obj.getint('simulate', 'cam_sum')
            self.comboBox_00.clear()
            self.comboBox_00.addItems(['虚拟相机%s' % i for i in range(cam_sum)])
        else:
            self.device_info = MV_CC_DEVICE_INFO_LIST()
            cam_sum = self.enumDevices()
        return cam_sum

    def createArgsListDict(self):
        """创建all_spinBox_list_dic参数列表"""
        _translate = QtCore.QCoreApplication.translate
        # 创建字典以储存所有spinBox的参数
        all_spinBox_list_dic = {}
        # 遍历 图像检测类 列表
        for n, image_detect_obj in enumerate(self.visual_detection_obj_list):
            args_dict = image_detect_obj.defineParams()
            camera_ini_obj = self.camera_config_obj_list[n]

            label_list = []
            all_spinBox_list_dic[n] = []

            for i, key in enumerate(args_dict):
                # 将变量名写入label
                label_list.append(QtWidgets.QLabel(self.args_list_obj_list[n]))
                label_list[i].setGeometry(QtCore.QRect(10, 40 * (i + 1), 120, 30))
                label_list[i].setObjectName("label_%s" % i)
                label_list[i].setText(_translate("MainWindow", key))

                # 将参数值写入SpinBox
                all_spinBox_list_dic[n].append(QtWidgets.QSpinBox(self.args_list_obj_list[n]))
                all_spinBox_list_dic[n][i].setGeometry(QtCore.QRect(130, 40 * (i + 1), 90, 30))

                all_spinBox_list_dic[n][i].setMinimum(camera_ini_obj.getint('param%s' % i, 'min'))
                all_spinBox_list_dic[n][i].setMaximum(camera_ini_obj.getint('param%s' % i, 'max'))
                all_spinBox_list_dic[n][i].setProperty("value", camera_ini_obj.getint('param%s' % i, 'value'))

                all_spinBox_list_dic[n][i].setObjectName('spinBox_%s' % i)
                all_spinBox_list_dic[n][i].valueChanged.connect(self.changeArgsDict)
        return all_spinBox_list_dic

    def getArgsListObjList(self):
        """创建参数列表"""
        _translate = QtCore.QCoreApplication.translate

        args_list_obj_list = []
        for n in range(self.cam_sum):
            groupBox_n = QtWidgets.QGroupBox(self.centralwidget)
            groupBox_n.setGeometry(QtCore.QRect(840, 90, 231, 631))
            groupBox_n.setStyleSheet("background-color: rgb(255, 255, 255);\n")
            groupBox_n.setAlignment(QtCore.Qt.AlignCenter)
            groupBox_n.setObjectName("groupBox_%s" % n)
            groupBox_n.setTitle(_translate("MainWindow", "参数列表%s" % n))
            # 加入列表
            args_list_obj_list.append(groupBox_n)
        return args_list_obj_list

    def getConfigPathList(self):
        """获取所有相机的配置文件路径列表"""
        type_dir_path = os.path.join(self.config_path, self.product_type)
        file_list = os.listdir(type_dir_path)
        config_path_list = []
        for i in range(self.cam_sum):
            file_name = f'camera{i}.ini'
            if file_name in file_list:
                config_path_list.append(os.path.join(type_dir_path, file_name))
            else:
                print(f'路径{os.path.abspath(type_dir_path)}下不存在相机{i}的配置文件{file_name}')
                exit(1)
        return config_path_list

    def getSystemParameter(self):
        """获取系统变量"""
        self.system_config_path = os.path.join(self.config_path, 'config.ini')
        self.system_config_obj = self.getConfigObj(self.system_config_path)

        self.run_mode = self.system_config_obj.getint('run', 'mode')
        self.save_mode = self.system_config_obj.getint('save', 'mode')
        self.save_type = self.system_config_obj.getint('save', 'type')

        self.save_path = self.system_config_obj.get('save', 'path')
        self.read_path = self.system_config_obj.get('read', 'path')

        self.user_password = self.system_config_obj.get('password', 'user')
        self.admin_password = self.system_config_obj.get('password', 'admin')

        self.product_type = self.system_config_obj['product']['type']
        self.product_list = self.system_config_obj['product']['list']

        self.control_rejector = self.system_config_obj.getboolean('control', 'rejector')
        self.control_port = self.system_config_obj.get('control', 'port')

    def getConfigObjList(self, config_path_list):
        """获取相机配置文件对象列表"""
        return [self.getConfigObj(config_path) for config_path in config_path_list]

    @staticmethod
    def getConfigObj(config_path):
        """获取配置文件对象"""
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf8')
        return config

    def showImageToMainLabelByPushButtonControl(self):
        """点击原图/处理图,显示图片到标签中(通过开关控制)"""
        if self.pushButton_01.isChecked():  # 是否选中
            self.show_image_control_list[self.now_show_num] = 2
            self.pushButton_01.setText('灰度图')
        else:
            self.show_image_control_list[self.now_show_num] = 1
            self.pushButton_01.setText('原始图像')
        # 从缓存图显示
        self.displayFromCache()

    @staticmethod
    def getTimeNumber():
        """获取序列时间"""
        return f"{time.time():.0f}"

    def errorStop(self):
        """出错暂停"""
        print("""出错暂停""")
        if self.pushButton_04.isChecked():
            # 权限验证
            if not self.confirmPassword(info='出错暂停'):
                return self.pushButton_04.setChecked(False)
            self.pushButton_04.setText('出错暂停')
            self.control_dict['ErrorStop'] = True
        else:
            self.pushButton_04.setText('出错继续')
            self.control_dict['ErrorStop'] = False

    def errorStop_CallbackFunction(self):
        """出错暂停的回调函数"""
        if self.pushButton_05.isChecked():
            self.pushButton_05.setChecked(False)
        self.startOrStopRun()

    def startUpdataCsv(self):
        """在线程中启动更新csv"""
        update_csv_thread = Thread(target=self.cyclicUpdateCsv)
        # 线程守护
        update_csv_thread.setDaemon(True)
        update_csv_thread.start()

    def cyclicUpdateCsv(self):
        """按时间循环更新"""
        num = 1
        while True:
            if self.trigger_count > 200:
                self.updateCsv()
                num += 1
            time.sleep(10)

    @staticmethod
    def getCsvPath():
        """获取csv路径"""
        now_time = datetime.datetime.now()
        year_month = now_time.strftime("%Y_%m")
        day = now_time.strftime("%d")
        dir_path = os.path.join('./File_CSV', year_month)
        csv_path = os.path.join(dir_path, day + '.csv')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        if not os.path.exists(csv_path):
            # 若csv文件不存在创建文件并添加表头
            with open(csv_path, 'a+', encoding='utf8') as f:
                f.write('批id, 次id, 异常数量, 总数,\n')
        return csv_path

    def updateAllCoordinates(self):
        """更新所有相机坐标"""
        for i in range(self.cam_sum):
            x1, y1, x2, y2 = self.train_coordinates_list[i]
            zoom_x, zoom_y = self.train_zoom_ratio_list[i]

            self.visual_detection_obj_list[i].args_dict['Coord'] = (int(x1 * zoom_x), int(y1 * zoom_y),
                                                                    int(x2 * zoom_x), int(y2 * zoom_y))
            self.visual_detection_obj_list[i].updateCoord()

    def getZoomRatioList(self):
        """获取缩放比例列表"""
        m_w, m_h = self.label_main.width(), self.label_main.height()
        return [[camera_ini_obj.getint('image', 'width') / m_w,
                 camera_ini_obj.getint('image', 'height') / m_h] for camera_ini_obj in self.camera_config_obj_list]

    def trainingMode(self):
        """训练模式"""
        if self.pushButton_06.isChecked():
            # 权限验证
            if not self.confirmPassword(info='训练模式'):
                return self.pushButton_06.setChecked(False)
            # 禁用单选按钮
            self.disabledRadioButton()
            self.pushButton_06.setText('保存坐标')
            # 开启捕捉
            self.label_main.setDrawRect(True)
        else:
            self.pushButton_06.setText('训练模式')
            # 关闭捕捉
            self.label_main.setDrawRect(False)
            # 获取坐标
            x1, y1, x2, y2 = self.trimCoordinates(*self.label_main.getCoord())
            # 存入训练坐标列表
            self.train_coordinates_list[self.now_show_num] = [x1, y1, x2, y2]
            # 存入配置文件
            self.updateCameraConfig(x1, y1, x2, y2)
            # 更新相机的坐标参数
            self.updateNowCoord(x1, y1, x2, y2)
            # 启用单选按钮
            self.enabledRadioButton()

    def updateCameraConfig(self, x1, y1, x2, y2):
        camera_ini_obj = self.camera_config_obj_list[self.now_show_num]
        camera_ini_obj['train']['x1'] = str(x1)
        camera_ini_obj['train']['y1'] = str(y1)
        camera_ini_obj['train']['x2'] = str(x2)
        camera_ini_obj['train']['y2'] = str(y2)

    def trimCoordinates(self, x1, y1, x2, y2):
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if x2 > self.label_main.width():
            x2 = self.label_main.width()
        if y2 > self.label_main.height():
            y2 = self.label_main.height()
        return x1, y1, x2, y2

    def updateNowCoord(self, x1, y1, x2, y2):
        """更新当前相机坐标"""
        zoom_x, zoom_y = self.train_zoom_ratio_list[self.now_show_num]
        self.visual_detection_obj_list[self.now_show_num].args_dict['Coord'] = [int(x1 * zoom_x), int(y1 * zoom_y),
                                                                                int(x2 * zoom_x), int(y2 * zoom_y)]
        self.visual_detection_obj_list[self.now_show_num].updateCoord()

    def getTrainCoordinatesList(self):
        """获取训练模式的坐标列表 [[x1,y1,x2,y2],[...]]"""
        return [[camera_ini_obj.getint('train', 'x1'),
                 camera_ini_obj.getint('train', 'y1'),
                 camera_ini_obj.getint('train', 'x2'),
                 camera_ini_obj.getint('train', 'y2')] for camera_ini_obj in self.camera_config_obj_list]

    def monitorSwitch(self):
        """监视状态"""
        if self.pushButton_08.isChecked():
            # 权限验证
            if not self.confirmPassword(info='修改参数'):
                return self.pushButton_08.setChecked(False)
            self.pushButton_08.setText('调整参数')
            for args_list_obj in self.args_list_obj_list:
                args_list_obj.setEnabled(True)
        else:
            self.pushButton_08.setText('监视状态')
            for args_list_obj in self.args_list_obj_list:
                args_list_obj.setEnabled(False)

    def createExceptionDirectory(self):
        """创建异常图像存储目录"""
        exception_path = os.path.join(self.save_path, 'exception')
        if os.path.exists(exception_path):
            if os.path.isdir(exception_path):
                pass
            else:
                os.remove(exception_path)
                os.mkdir(exception_path)
        else:
            os.mkdir(exception_path)
        return exception_path

    def deleteExceptionDirectory(self):
        """删除异常图片存储目录"""
        if os.path.exists(self.exception_path):
            shutil.rmtree(self.exception_path)

    def closeAllCamera(self):
        """关闭所有相机"""
        if self.is_open:
            for camera_obj in self.camera_operation_obj_list:
                camera_obj.closeCamera()
            self.is_open = False
            print('相机已关闭~')

    def rejectorSwitch(self):
        """剔除开关"""
        if self.pushButton_07.isChecked():
            # 权限验证
            if not self.confirmPassword(info='开启剔除'):
                return self.pushButton_07.setChecked(False)
            self.pushButton_07.setText('剔除开')
            self.control_dict['Rejector'] = True
            self.system_config_obj['control']['rejector'] = '1'
        else:
            if not self.confirmPassword(info='关闭剔除'):
                return self.pushButton_07.setChecked(True)
            self.pushButton_07.setText('剔除关')
            self.control_dict['Rejector'] = False
            self.system_config_obj['control']['rejector'] = '0'

    def setRejectorButton(self):
        """设置剔除按钮"""
        self.control_dict['Rejector'] = self.control_rejector

        if self.control_dict['Rejector']:
            self.pushButton_07.setText('剔除开')
            self.pushButton_07.setChecked(True)

    def confirmPassword(self, utype='user', info="权限验证"):
        """检查密码的函数, 密码正确返回True"""

        if utype == 'admin':
            value, ok = QInputDialog.getText(self, info, "请输入管理员密码~", QLineEdit.Password)
            password = self.admin_password
        else:
            value, ok = QInputDialog.getText(self, info, "请输入用户密码~", QLineEdit.Password)
            password = self.user_password

        if ok:
            if value == password:
                return True
            elif QMessageBox.warning(self, "密码错误!", "密码应为1~6位字符!\n是否重试?",
                                     QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                return self.confirmPassword(utype, info)

    def selectSimulateRun(self):
        """选择模拟运行"""
        if self.run_mode == 0:
            if self.checkBox.isChecked():

                # 禁用"启动"按钮
                self.pushButton_05.setEnabled(False)
                # 循环开启取流
                self.startAllGrabbing()
            else:
                # = False
                # 解禁"启动"按钮
                self.pushButton_05.setEnabled(True)
                # 停止抓取
                self.stopAllGrabbing()

    def startOrStopRun(self):
        """启动 或 停止 程序"""

        # 未检测到相机时终止运行
        if not self.cam_sum:
            self.pushButton_05.setChecked(False)
            return QMessageBox(QMessageBox.Warning, '警告', '未检测到相机!').exec_()
        if self.pushButton_05.isChecked():
            self.startRun()
            self.pushButton_05.setText('停止运行')
            self.is_run = True
        else:
            self.stopRun()
            self.is_run = False
            self.pushButton_05.setText('运行程序')
        # 保存CSV
        self.updateCsv()

    def stopRun(self):
        if self.is_run:
            if self.run_mode == 2:
                self.stopAllGrabbing()
            else:
                self.stopTrigger()

    def startRun(self):
        if not self.is_run:
            if self.run_mode == 2:
                # 循环开启取流
                self.startAllGrabbing()
            else:
                self.startTrigger()

    def startTrigger(self):
        """启动编码器触发"""

        # 禁用复选按钮
        self.checkBox.setEnabled(False)
        # 初始化控制变量
        self.sensor_control_obj.run_sensor_control = True
        self.sensor_signal_trigger_Control = True
        # 循环开启取流
        self.startAllGrabbing()
        # 传感器获取信号: 创建线程循环等待获取传感器信号
        get_sensor_signal_handle = Thread(target=self.signal_CallbackFunction,
                                          args=(self.trigger_CallbackFunction,))
        # 线程守护
        get_sensor_signal_handle.setDaemon(True)
        # 开启线程
        get_sensor_signal_handle.start()

    def startAllGrabbing(self):
        """循环开启取流"""
        if not self.is_run:
            for camera_obj in self.camera_operation_obj_list:
                camera_obj.startGrabbing()

    def piecewiseTriggerOnce(self, serial_number: int):
        """分段触发一次"""
        num = serial_number // 20
        try:
            print(f'--> 传感器信号{serial_number}, 触发相机{num}采图 <--')
            self.camera_operation_obj_list[num].triggerOnce(serial_number)
        except Exception as e:
            info = f'{e}\n参数越界:编号{serial_number} 调用相机{num}失败!\nMain.piecewiseTriggerOnce'
            self.messageBox(info)
            exit(1)
        # 更新界面上的计数
        self.count += 1
        self.showCountToLabelCount()

    def stopTrigger(self):
        """停止编码器触发"""
        # 解禁复选按钮
        self.checkBox.setEnabled(True)
        # 停止收集传感器信号
        self.sensor_control_obj.run_sensor_control = False
        # 停止抓取
        self.stopAllGrabbing()

    def showNowModeToLabel(self):
        """在标签中显示当前模式"""
        self.checkBox.setHidden(True)
        if self.run_mode == 1:
            self.label_mode.setText('时间模式')
        elif self.run_mode == 2:
            self.label_mode.setText('模拟运行')

    def setCameraArgs(self):
        """设置相机参数"""

        self.pushButton_05.setChecked(False)
        self.pushButton_05.setText('运行程序')

        if self.run_mode == 0 or self.run_mode == 1:
            self.stopAllGrabbing()  # 循环停止抓取

        # 初始化系统配置
        self.getSystemParameter()
        # 分模式运行
        self.runByMode()

    def saveConfig(self):
        """持久化参数到配置文件"""
        self.saveCameraConfig()
        self.saveSystemConfig()

    def saveSystemConfig(self):
        """写入系统参数"""
        with open(self.system_config_path, 'w', encoding='utf8') as f:
            self.system_config_obj.write(f)
        print('系统配置文件已保存~')

    def saveCameraConfig(self):
        """写入相机参数"""

        # 遍历图像检测对象
        for i, image_detect_obj in enumerate(self.visual_detection_obj_list):
            # 遍历 修改参数列表
            for j in range(len(image_detect_obj.args_dict['SpinBox'])):
                self.camera_config_obj_list[i]['param%s' % j]['value'] = str(image_detect_obj.args_dict['SpinBox'][j])
            # 将对象写入文件
            with open(self.camera_config_path_list[i], 'w', encoding='utf8') as f:
                self.camera_config_obj_list[i].write(f)
        print('相机配置文件已保存~')

    def stopAllGrabbing(self):
        """停止抓取"""
        if self.is_run:
            for camera_obj in self.camera_operation_obj_list:
                camera_obj.stopGrabbing()
            print('已停止抓取~')

    def openAllCamera(self):
        """打开相机"""
        if not self.is_open:
            print('\n打开相机:')
            ret = 0
            for cam_obj in self.camera_operation_obj_list:
                ret += cam_obj.openCamera()
            if ret:
                pass
            else:
                self.is_open = True

    def reopenAllCamera(self):
        # 重新打开
        print('\n重开相机:')
        ret = 0
        for camera_obj in self.camera_operation_obj_list:
            camera_obj.stopGrabbing()
            camera_obj.closeCamera()
            ret += camera_obj.openCamera()
        if ret:
            self.is_open = False
        else:
            self.is_open = True

    def changeArgsDict(self):
        """改变参数字典: 向VisualDetection.py下的VisualDetection类的self.args_dict['SpinBox']传值,该值将在退出时保存"""
        cam_num = self.now_show_num
        spinBox_obj_list = self.all_spinBox_list_dic[cam_num]
        # 图像检测类
        image_detect_obj = self.visual_detection_obj_list[cam_num]
        # 循环写入
        for i, spinBox_obj in enumerate(spinBox_obj_list):
            # 将参数传入图像检测类
            image_detect_obj.args_dict['SpinBox'][i] = spinBox_obj.value()
        # 使生效:局部变量全局化
        image_detect_obj.updateVariate()
        # 调用缓存图
        self.displayFromCache()

    def setComboBoxBySimulateTrigger(self):
        """通过模拟触发设置下拉表单的显示内容"""
        self.comboBox_00.clear()
        self.comboBox_00.addItems(['虚拟相机%s' % i for i in range(self.cam_sum)])

    def showCountToLabelCount(self):
        text = f'计数: {self.count}'
        self.label_count.setText(text)

    def allCameraTriggerOnce(self, serial_number):
        # 所有相机都触发一次
        for self.camera_obj in self.camera_operation_obj_list:
            self.camera_obj.triggerOnce(serial_number)
        # 更新界面上的计数
        self.count += 1
        self.showCountToLabelCount()

    def changeShift(self):
        # 保存csv
        self.updateCsv()
        self.batch_time_number = self.getTimeNumber()
        # 清空计数
        self.count = 0
        self.showCountToLabelCount()

    def updateCsv(self):
        """更新csv"""
        trigger_count, self.trigger_count = self.trigger_count, 0

        result_text_list = []
        for item in self.all_camera_result_text_dict:
            result_text_list.append(self.all_camera_result_text_dict[item])
            self.all_camera_result_text_dict[item] = {}

        all_number_dict = {}
        for item in result_text_list:
            all_number_dict.update(item)

        erroe_count = len(all_number_dict)

        self.writeCSV(erroe_count, trigger_count)
        print('--> 保存CSV完成 <--')

    def writeCSV(self, erroe_count, trigger_count):
        """写入csv '批id, 次id, 异常数量, 总数,\n' """
        with open(self.csv_path, 'a+', encoding='utf8') as file_obj:
            file_obj.write(f'{self.batch_time_number},{self.getTimeNumber()},{erroe_count},{trigger_count},\n')

    def showNowCameraArgslist(self):
        """显示当前相机的参数列表"""
        for i, args_list_obj in enumerate(self.args_list_obj_list):
            if i == self.now_show_num:
                print('参数列表%s   显示' % i)
                args_list_obj.setVisible(True)
            else:
                args_list_obj.setVisible(False)

    def showImageToMainLabelByRadioButtonControl(self):
        """点击相机单选按钮,显示图片到主标签(通过开关控制)"""
        for i, control_bool in enumerate(self.show_image_control_list):
            if control_bool:
                self.show_image_control_list[i] = False

        if self.pushButton_01.isChecked():  # 是否选中
            self.show_image_control_list[self.now_show_num] = 2
        else:
            self.show_image_control_list[self.now_show_num] = 1

    def changNowCamera(self, cam_num):
        """变更当前相机:param cam_num:相机编号"""
        if not self.cam_sum:
            return
        # 重置当前编号
        self.now_show_num = cam_num
        # 显示当前编号的 参数列表
        self.showNowCameraArgslist()
        # 显示当前编号的图像
        self.showImageToMainLabelByRadioButtonControl()
        # 从缓存显示
        self.displayFromCache()
        # 显示训练模式下的矩形区域
        self.label_main.updateRect(*(self.train_coordinates_list[self.now_show_num]))

    def enumDevices(self):
        """枚举设备"""
        dev_list = []
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, self.device_info)

        if ret != 0:
            # 弹框抛出异常
            msg_box = QMessageBox(QMessageBox.Warning, 'error!', '枚举设备失败!')
            msg_box.exec_()
        else:
            self.comboBox_00.clear()
        if self.device_info.nDeviceNum == 0:
            self.comboBox_00.addItem('未发现设备!')
            return 0
        else:
            print("找到%d个设备:" % self.device_info.nDeviceNum)
        # 设备列表
        for i in range(0, self.device_info.nDeviceNum):
            mvcc_dev_info = cast(self.device_info.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                strModeName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                    strModeName = strModeName + chr(per)
                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("\t相机%s: %s" % (i, strModeName,))
                print("\tIP: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
                dev_list.append("相机" + str(i) + "  " + str(nip1) + "." + str(nip2) + "." + str(nip3) + "." + str(nip4))
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nu3v 设备: [%d]" % i)
                strModeName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                    if per == 0:
                        break
                    strModeName = strModeName + chr(per)
                print("设备型号: %s" % strModeName)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("客户编号: %s" % strSerialNumber)
                dev_list.append("USB[" + str(i) + "]" + str(strSerialNumber))
        # 将设备列表写入下拉表单
        self.comboBox_00.addItems(dev_list)
        return len(dev_list)

    def getSleepTimeList(self):
        """ 获取休眠时间列表: 用于"模拟运行" """
        sleep_time_list = []
        for camera_ini_obj in self.camera_config_obj_list:
            frame_rate = camera_ini_obj.getint('camera', 'framerate')
            sleep_time_list.append(1 / frame_rate)
        return sleep_time_list

    def Window_ExceptionImage(self):
        """显示异常图片"""

        from Child_ExceptionImage.ExceptionImage import ExceptionImage
        ExceptionImage(exception_dir=self.exception_path).exec()

    def Window_SaveMode(self):
        """更改保存图像模式"""

        # 权限验证
        if not self.confirmPassword(info='更改保存图像模式'):
            return

        from Child_SaveMode.SaveMode import showSaveModeWindow
        # 重启
        if showSaveModeWindow(config_ini_path=self.system_config_path, config_ini_obj=self.system_config_obj):
            # 选择重启
            if QMessageBox.warning(self, "重启!", "图像保存模式已更改! 重启生效!\n是否重启?",
                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.__DirectlyRestart()

        # else:
        #     # 更新存图模式字典
        #     self.updateSaveImageModeDict()

    def Window_SystemConfig(self):
        """显示系统配置"""

        # 权限验证
        if not self.confirmPassword(utype='admin', info='系统配置'):
            return

        from Child_SystemConfig.SystemConfig import showSystemConfigWindow
        # 重启
        if showSystemConfigWindow(config_ini_path=self.system_config_path, config_ini_obj=self.system_config_obj):

            if QMessageBox.warning(self, "重启", "系统参数已更改! 重启生效\n是否重启?",
                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.__DirectlyRestart()

    def Window_CameraConfig(self):
        """相机配置: 映射"相机配置"按钮, 打开相机参数界面"""

        # 拦截无相机
        if self.cam_sum == 0:
            return QMessageBox.about(self, '无相机', '未检测到相机,该项不能设置!')
        # 权限验证
        if not self.confirmPassword(info='相机配置'):
            return
        from Child_CameraConfig.CameraConfig import showCameraConfigWindow
        # 判断是否设置参数
        if showCameraConfigWindow(cam_sum=self.cam_sum,
                                  cam_num=self.now_show_num,
                                  cam_ini_obj_list=self.camera_config_obj_list):
            if QMessageBox.warning(self, "重启", "相机参数已更改! 重启生效\n是否重启?",
                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.__DirectlyRestart()

    def Window_ChangeProduct(self):
        """更换产品"""

        # 权限验证
        if not self.confirmPassword(info='更换产品'):
            return

        from Child_ChangeProduct.SelectProdcut import showSelectProductWindow

        if showSelectProductWindow(config_ini_path=self.system_config_path,
                                   config_ini_obj=self.system_config_obj):
            # 选择重启
            if QMessageBox.warning(self, "重启", "产品已变更! 重启生效!\n是否重启?",
                                   QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.__DirectlyRestart()

    def __ReadyQuit(self):
        """准备离开: 内部调用,结束任务"""

        # 持久化参数到文件
        self.saveConfig()
        # 停止抓取
        self.stopRun()
        # 关闭所有相机
        self.closeAllCamera()
        # 保存csv
        self.updateCsv()

    def __DirectlyRestart(self):
        """直接重启: 内部调用"""
        self.__ReadyQuit()
        # 返回重启编号
        QApplication.exit(6)

    def restartDevice(self):
        """重启设备"""
        if not self.confirmPassword(info='重启设备'):
            return
        print('\n重启相机:')
        self.__DirectlyRestart()

    def closeDevice(self):
        """关闭设备"""
        if not self.confirmPassword(info='退出系统'):
            return
        print('\n关闭相机:')
        self.__ReadyQuit()
        # 删除缓存目录
        self.deleteExceptionDirectory()
        exit(0)

    def closeEvent(self, event):
        # 权限验证
        if self.confirmPassword(info='关闭'):
            self.__ReadyQuit()
            # 删除缓存目录
            self.deleteExceptionDirectory()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """重写按键事件"""
        if event.key() == QtCore.Qt.Key_Escape:
            self.closeDevice()
        elif event.key() == QtCore.Qt.Key_F12:
            # 若"模拟运行"按钮未选中
            if self.checkBox.isChecked():
                # 触发一次
                self.allCameraTriggerOnce(-1)

    def getAllCameraImagePathListList(self):
        """获取所有相机图像路径列表的列表: 仅用于模拟触发"""
        all_camera_image_path_list_list = []
        item_list = os.listdir(self.read_path)
        root_dir_img_path_list = []
        sub_dir_list = []
        # 获得根目录下的图片路径列表 和 子目录列表
        for item in item_list:
            item_path = os.path.join(self.read_path, item)
            if item.split('.')[-1].lower() in ['jpg', 'png', 'bmp', 'jpeg']:
                root_dir_img_path_list.append(item_path)
            elif os.path.isdir(item_path):
                sub_dir_list.append(item)
        for i in range(self.cam_sum):
            camera_n = 'camera%s' % i
            if camera_n in sub_dir_list:
                all_camera_image_path_list_list.append(self.getAllImagePathList(os.path.join(self.read_path, camera_n)))
            else:
                all_camera_image_path_list_list.append(root_dir_img_path_list)
        return all_camera_image_path_list_list

    @staticmethod
    def getAllImagePathList(path):
        image_path_list = []
        for item in os.listdir(path):
            if item.split('.')[-1].lower() in ['jpg', 'png', 'bmp', 'jpeg']:
                image_path_list.append(os.path.join(path, item))
        return image_path_list

    @staticmethod
    def TxtWrapBy(start_str, end, _all):
        """获取选取设备信息的索引，通过[]之间的字符去解析"""
        start = _all.find(start_str)
        if start >= 0:
            start += len(start_str)
            end = _all.find(end, start)
            if end >= 0:
                return _all[start:end].strip()

    def hideRadioButton(self, cam_sum):
        """显示与隐藏相机单选按钮: 按相机个数"""
        if cam_sum <= 0:
            self.radioButton_0.setVisible(False)
        else:
            self.radioButton_0.setVisible(True)
        if cam_sum <= 1:
            self.radioButton_1.setVisible(False)
        else:
            self.radioButton_1.setVisible(True)
        if cam_sum <= 2:
            self.radioButton_2.setVisible(False)
        else:
            self.radioButton_2.setVisible(True)
        if cam_sum <= 3:
            self.radioButton_3.setVisible(False)
        else:
            self.radioButton_3.setVisible(True)
        if cam_sum <= 4:
            self.radioButton_4.setVisible(False)
        else:
            self.radioButton_4.setVisible(True)
        if cam_sum <= 5:
            self.radioButton_5.setVisible(False)
        else:
            self.radioButton_5.setVisible(True)

    def disabledRadioButton(self):
        """禁用单选按钮"""
        self.radioButton_0.setEnabled(False)
        self.radioButton_1.setEnabled(False)
        self.radioButton_2.setEnabled(False)
        self.radioButton_3.setEnabled(False)
        self.radioButton_4.setEnabled(False)
        self.radioButton_5.setEnabled(False)

    def enabledRadioButton(self):
        """启用单选按钮"""
        self.radioButton_0.setEnabled(True)
        self.radioButton_1.setEnabled(True)
        self.radioButton_2.setEnabled(True)
        self.radioButton_3.setEnabled(True)
        self.radioButton_4.setEnabled(True)
        self.radioButton_5.setEnabled(True)

    @staticmethod
    def messageBox(info='未知错误!', title='错误!'):
        return QMessageBox(QMessageBox.Critical, title, info).exec_()


def showMainWindow():
    # app = QApplication(sys.argv)
    app = QApplication([])
    main_window = Main()
    main_window.show()
    sys.exit(app.exec_())
