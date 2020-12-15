from PyQt5.QtWidgets import QInputDialog, QMessageBox, QLineEdit


def passwordCheck(function, type):
    """检查密码的装饰器"""

    def wrapper(self, *args, **kwargs):
        value, ok = QInputDialog.getText(self, "退出系统", "请输入用户密码~", QLineEdit.Password)
        if not ok:
            return
        if value != self.user_password:
            if QMessageBox.warning(self, "密码错误!", "密码应为1~6位字符!\n是否重试?", QMessageBox.Yes | QMessageBox.No) == 16384:
                return wrapper(self, *args, **kwargs)
            else:
                return
        function(self)

    return wrapper


def confirmPassword_Decorator(type='user'):
    """检查密码的装饰器"""

    def transferFunction(function):

        def wrapper(self, *args, **kwargs):
            if type == 'admin':
                value, ok = QInputDialog.getText(self, "权限验证", "请输入管理员密码~", QLineEdit.Password)
                password = self.admin_password
            else:
                value, ok = QInputDialog.getText(self, "权限验证", "请输入用户密码~", QLineEdit.Password)
                password = self.user_password
            if ok:
                if value == password:
                    return function(self)
                else:
                    if QMessageBox.warning(self, "密码错误!", "密码应为1~6位字符!\n是否重试?",
                                           QMessageBox.Yes | QMessageBox.No) == 16384:
                        return wrapper(self, *args, **kwargs)

        return wrapper

    return transferFunction
