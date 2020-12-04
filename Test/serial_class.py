import os


class Statistics:
    def __init__(self):
        self.project_dir = 'Frame2.3'
        self.type_list = ['.py', '.c', '.h', '.cpp', '.hpp', ]
        self.file_list = []
        self.sum = 0
        self.operation()

    def operation(self):
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
