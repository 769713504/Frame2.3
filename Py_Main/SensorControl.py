# -- coding: utf-8 --
"""传感器控制类"""
import random
import time

import serial


class SensorSerialPortControl:
    """传感器串口控制类"""

    def __init__(self, port='com3'):
        self.run_sensor_control = True
        self.run_time_control = False
        self.sleep_time = 0.2
        self.trigger_mode = self.setTriggerMode(port)

    def setTriggerMode(self, port):
        try:
            self.serial_obj = serial.Serial(port=port, baudrate=19200, timeout=None)
            print(f'=============== 端口[{port}]已连接~ ===============')
            return True
        except:
            print(f'=============== 端口[{port}]不可用! ===============')
            # exit(0)

    # todo 编码器 #######################################################################################################
    def getSensorSignal(self, PiecewiseTriggerOnce_MainWindowFunction):
        """获取传感器信号"""
        print("虚拟连接666")
        while self.run_sensor_control:
            time.sleep(0.1)
            code = random.randint(0, 39)
            # 在主窗口中循环触发一次
            PiecewiseTriggerOnce_MainWindowFunction(code)
        print('传感器信号采集模块,退出')

        # while self.run_sensor_control:
        #     byte = self.serial_obj.read()
        #     code = int.from_bytes(byte, byteorder='little', signed=True)
        #     # 在主窗口中循环触发一次
        #     PiecewiseTriggerOnce_MainWindowFunction(code)
        # print('传感器信号采集模块,退出')

    def triggerSensorRejector(self, serial_number: int):
        """触发传感器剔除"""
        byte = serial_number.to_bytes(1, byteorder='little', signed=False)
        if self.trigger_mode:
            print(f'--> [剔除器]触发剔除! 编号{serial_number},发送指令{byte} <--')
            self.serial_obj.write(byte)
        else:
            print(f"--> [剔除器]传感器未连接,剔除未发送! 编号:{serial_number},指令{byte} <--")

    # todo 时间 ########################################################################################################
    def getTimeSignal(self, AllTriggerOnce_MainWindowFunction):
        code = 0
        while self.run_sensor_control:
            code += 1
            # 在主窗口中循环触发一次
            print('时间信号:%s, 触发...' % code)
            AllTriggerOnce_MainWindowFunction(code)
            time.sleep(self.sleep_time)
        print('时间信号采集模块,退出')

    def timeSimulationRejector(self, num):
        """时间模拟剔除"""
        serial_number = random.randint(0, 19)
        byte = serial_number.to_bytes(1, byteorder='little', signed=False)
        if self.trigger_mode:
            print(f'--> [时间模拟{num}]触发剔除! 编号{serial_number},发送指令{byte} <--')
            self.serial_obj.write(byte)
        else:
            print(f"--> [时间模拟{num}]传感器未连接,剔除未发送! 编号:{serial_number},指令{byte} <--")
