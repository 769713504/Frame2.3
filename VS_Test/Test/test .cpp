#include <iostream>
#include <Python.h>

using namespace std;

int main()
{
	//��ʼ��
	Py_Initialize();

	if (!Py_IsInitialized()) {
		printf("��ʼ��ʧ�ܣ�");
		return 0;
	}

	//�޸�Python·��
	PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('./')");

	//��������
	PyObject* pModule = NULL;
	PyObject* pFunc1 = NULL;// ��������

	//ʵ�����ļ�
	//�ļ�����Ҫ����չ, ��������Ҫ������
	pModule = PyImport_ImportModule("Run");
	if (pModule == NULL) {
		cout << "û�ҵ�" << endl;
	}

	//ʵ��������
	pFunc1 = PyObject_GetAttrString(pModule, "run");
	//�����޷���ֵ����
	PyEval_CallObject(pFunc1, NULL);//�����޲����޷���ֵ��python����


	//���: ���ʼ����Ӧ
	Py_Finalize();


	return 0;

}
