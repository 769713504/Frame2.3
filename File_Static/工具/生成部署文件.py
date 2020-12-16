# -- coding: utf-8 --
import compileall
import os
import re
import shutil


class DeployProject:
    """部署项目"""

    def __init__(self):
        # 项目路径
        self.project_path = os.path.abspath('./').split('File_Static')[0]
        # 清理目录: 以?开头
        self.clear_dir_list = ['.', 'vs', 'vs2019', 'File_CSV', '.vs', '工具']
        # 清理文件件: 以?扩展
        self.clear_file_list = ['ui', 'pyproj', 'vcxproj', 'exe']
        # 选择解释器
        self.compiler = 'python37'
        # 编译目录
        self.compile_dir = '__pycache__'
        # 启动程序
        self.run_name = 'Run.py'
        # 文件列表
        self.file_list = []
        # 拷贝项目
        self.copyProject(self.project_path)
        # 获取py文件列表
        self.getPyFilePathList(self.project_path)
        # 删除注释
        self.removeComments(self.file_list)
        # 编译
        self.compileFile(self.project_path)
        # 移动字节码
        self.movePyc(self.file_list)
        # 清理不需要的目录和文件
        self.clearDirAndFile(self.project_path)
        # 更改启动程序名
        self.changeRunName(self.run_name)

    # 更改启动程序名
    def changeRunName(self, run_name):
        name = run_name.split('.')[0]
        run_name_path = os.path.join(self.project_path, name)
        shutil.move(run_name_path + '.pyc', run_name_path + '.pyw')
        print(f'--> 部署项目已生成~  位置:{self.project_path} <--')

    # 清理指定文件
    def clearDirAndFile(self, dir_path):
        file_list = os.listdir(dir_path)

        for file_name in file_list:
            file_path = os.path.join(dir_path, file_name)
            # 若为目录
            if os.path.isdir(file_path):

                if self.isCacheDir(file_name):
                    shutil.rmtree(file_path)
                else:
                    # 递归
                    self.clearDirAndFile(file_path)
            # 若为文件
            else:
                if file_name.split('.')[-1].lower() in self.clear_file_list:
                    os.remove(file_path)

    def isCacheDir(self, name):
        # 判断缓存
        for item in self.clear_dir_list:
            if name.lower().startswith(item):
                return True

    # 替换文件
    def movePyc(self, file_list):
        # 获取编译目录字典
        pyc_dict = set()
        for file_path in file_list:
            old_path = os.path.abspath(os.path.join(os.path.dirname(file_path), self.compile_dir))
            pyc_dict.add(old_path)
        # 解释器版本关键字
        edition = self.compiler.split('python')[-1].split('.')[-1]
        # 遍历编译目录
        for pyc_dir in pyc_dict:
            pyc_list = os.listdir(pyc_dir)
            for name in pyc_list:
                if name.split('-')[-1].split('.')[0] != edition:
                    continue
                old_path = os.path.join(pyc_dir, name)
                new_name = name.split('.')[0] + '.pyc'
                new_path = os.path.join(os.path.join(os.path.dirname(pyc_dir), new_name))
                # 移动文件
                shutil.move(old_path, new_path)

        self.clear_file_list.append('py')
        self.clear_dir_list.append(self.compile_dir)
        self.clear_file_list = [item.lower() for item in self.clear_file_list]
        self.clear_dir_list = [item.lower() for item in self.clear_dir_list]
        print('--> pyc转移完成~ <--')

    # 编译项目
    @staticmethod
    def compileFile(project_path):
        compileall.compile_dir(project_path)
        print('--> 编译完成~ <--')

    # 删除注释
    @staticmethod
    def removeComments(file_list):
        for file_path in file_list:
            with open(file_path, 'r', encoding='utf8') as read_file, \
                    open(file_path + '2', 'w', encoding='utf8') as write_file:
                # 写入编码方式
                write_file.write('# -- coding: utf-8 --\n')
                for line in read_file:
                    line_list = line.split()
                    # 非空行
                    if line_list:
                        # 1. 剔除"#"注释
                        if "#" in line:
                            # 开头#
                            if "#" is line_list[0]:
                                continue
                            # 中间#
                            else:
                                if "'" in line or '"' in line:
                                    write_file.write(line)
                                    continue
                                line_str = ''
                                for i in line:
                                    if i == '#':
                                        line_str += '\n'
                                        break
                                    else:
                                        line_str += i
                                write_file.write(line_str)
                                continue
                        # 2. 剔除"""注释
                        elif '"""' in line_list[0] or "'''" in line_list[0]:
                            try:
                                if re.match(r"[^\"]*\"\"\"[^\"]*\"\"\"", line)[0]:
                                    continue
                            except:
                                pass
                        else:
                            write_file.write(line)
            os.remove(file_path)
            os.rename(file_path + '2', file_path)
        print('--> 取消注释完成~ <--')

    # 获取文件列表,并筛选文件
    def getPyFilePathList(self, dir_path):
        file_list = os.listdir(dir_path)
        for file_name in file_list:
            file_path = os.path.join(dir_path, file_name)
            # 若为目录
            if os.path.isdir(file_path):
                # 递归
                self.getPyFilePathList(file_path)
            elif os.path.isfile(file_path):
                if file_name.split('.')[-1].lower() == 'py':
                    file_path = os.path.abspath(file_path)
                    self.file_list.append(file_path)

    # 拷贝项目
    def copyProject(self, project_path):
        # 生成部署项目路径
        project_path = os.path.abspath(project_path)
        deploy_path = os.path.join(os.path.dirname(project_path), os.path.basename(project_path) + "_deploy")
        # 创建部署目录
        if os.path.exists(deploy_path):
            shutil.rmtree(deploy_path)
        os.makedirs(deploy_path)
        # 拷贝目录
        for name in os.listdir(project_path):
            old_path = os.path.join(project_path, name)
            new_path = os.path.join(deploy_path, name)
            # 是文件
            if os.path.isfile(old_path):
                # 直接拷贝
                shutil.copy(old_path, new_path)
            # 是缓存
            elif self.isCacheDir(name):
                pass
            # 有效目录
            else:
                shutil.copytree(old_path, new_path)

        self.project_path = deploy_path
        print('--> 项目创建完成~ <--')


DeployProject()
