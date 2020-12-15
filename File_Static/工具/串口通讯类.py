# -- coding: utf-8 --
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
