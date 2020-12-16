# -- coding: utf-8 --
import os
import shutil


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
    DeleteCache()
