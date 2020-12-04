# -- coding: utf-8 --
import os
import shutil

import serial
import serial.tools.list_ports


class SerialPortCommunication:
    """串口通讯类: RS232DB9"""

    # 初始化
    def __init__(self, com: str, bps=19200, timeout=None):
        self.serial_obj = serial.Serial(com, bps, timeout=timeout)

    def printSettingsInfo(self):
        """打印设备信息"""
        return print(f'设备名:{self.serial_obj.name},读写端口:{self.serial_obj.port},波特率:{self.serial_obj.baudrate},'
                     f'字节大小:{self.serial_obj.bytesize},校验位:{self.serial_obj.parity},停止位:{self.serial_obj.stopbits},'
                     f'读超时:{self.serial_obj.timeout},写超时{self.serial_obj.writeTimeout},字符间隔超时:{self.serial_obj.interCharTimeout}')

    def openSerialPort(self):
        """打开串口"""
        return self.serial_obj.open()

    #
    def closeSerialPort(self):
        """关闭串口"""
        return self.serial_obj.close()

    def readSize(self, size):
        """接收指定大小的数据:从串口读size个字节。如果指定超时，则可能在超时后返回较少的字节；如果没有指定超时，则会一直等到收完指定的字节数"""
        return self.serial_obj.read(size=size)

    def readLine(self):
        """接收一行:使用readline()时应该注意：打开串口时应该指定超时(否则如果串口没有收到新行，则会一直等待)，若无超时 则readline异常"""
        return self.serial_obj.readline()

    #
    def sendData(self, data):
        """发数据"""
        return self.serial_obj.write(data)

    def receiveData(self, way=True):
        """循环接收数据"""
        while True:
            if self.serial_obj.in_waiting:
                if way:
                    # 整体接收
                    data = self.serial_obj.read_all()
                    yield data
                else:
                    # 单字节的接收
                    for i in range(self.serial_obj.in_waiting):
                        print("接收ascii数据：" + str(self.readSize(1)))
                        data = self.readSize(1).hex()  # 转为十六进制
                        yield data

    # 打印可用串口列表
    @staticmethod
    def Print_Used_Com():
        port_list = list(serial.tools.list_ports.comports())
        print(port_list)


def runSerialPortCommunication():
    serial_obj = SerialPortCommunication("com3")
    serial_obj.printSettingsInfo()
    # 接收
    for i in serial_obj.receiveData():
        i = i.decode("GBK")
        print(i)


class Statistics:
    """统计项目行数"""

    def __init__(self):
        self.project_dir = 'Frame2.3'
        self.type_list = ['.py', '.c', '.h', '.cpp', '.hpp', ]
        self.file_list = []
        self.sum = 0
        self.run()

    def run(self):
        project_path = os.path.join(os.path.abspath('.').split(self.project_dir)[0], self.project_dir)
        self.getFilepath(project_path)
        self.lineCount()

        print(f'\033[31m{len(self.file_list)}个文件,共计{self.sum}行')

    def getFilepath(self, path):
        # now_path=path
        now_file_list = os.listdir(path)
        for item in now_file_list:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                self.getFilepath(item_path)
            elif os.path.isfile(item_path):
                if '.' + item.split('.')[-1].lower() in self.type_list:
                    self.file_list.append(item_path)

    def lineCount(self):
        for file in self.file_list:
            count = 0  # 让空文件的行号显示0
            with open(file, 'rb+') as f:
                for _ in f:
                    count += 1
            self.sum += count


class DeleteCache:
    """删除缓存文件"""

    def __init__(self):
        self.project_dir = '版本'
        self.type_list = ['.', '__pyc', 'debug', 'Relese', 'x64']

        self.run()

    def run(self):
        self.file_list = []

        effect_path = os.path.join(os.path.abspath('.').split(self.project_dir)[0], self.project_dir)
        self.getDirPath(effect_path)
        print(self.file_list)
        self.deleteTarget()

    def deleteTarget(self):
        for item in self.file_list:
            try:
                shutil.rmtree(item)
            except Exception as e:
                print(e)
                print(item)

    def frontInTypeList(self, file_name):
        for item in self.type_list:
            if file_name.lower().startswith(item.lower()):
                return True

    def getDirPath(self, path):
        # now_path=path
        now_file_list = os.listdir(path)
        for file_name in now_file_list:
            file_path = os.path.join(path, file_name)
            if os.path.isdir(file_path):
                if self.frontInTypeList(file_name):

                    self.file_list.append(file_path)
                else:
                    self.getDirPath(file_path)


if __name__ == '__main__':
    # DeleteCache()
    Statistics()
