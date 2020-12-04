#include <iostream>
#include <Python.h>

using namespace std;

int main()
{
	//初始化
	Py_Initialize();

	if (!Py_IsInitialized()) {
		printf("初始化失败！");
		return 0;
	}

	//修改Python路径
	PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('./')");

	//声明变量
	PyObject* pModule = NULL;
	PyObject* pFunc1 = NULL;// 声明变量

	//实例化文件
	//文件名不要加扩展, 函数名不要加括号
	pModule = PyImport_ImportModule("Run");
	if (pModule == NULL) {
		cout << "没找到" << endl;
	}

	//实例化函数
	pFunc1 = PyObject_GetAttrString(pModule, "run");
	//调用无返回值函数
	PyEval_CallObject(pFunc1, NULL);//调用无参数无返回值的python函数


	//完成: 与初始化对应
	Py_Finalize();


	return 0;

}
