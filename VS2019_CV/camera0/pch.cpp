#include "pch.h"

// Todo 四、根据界面参数 声明变量.
int val_1;
int val_2;
int val_3;
int val_4;
int val_5;
int val_6;


void updateArgs(int   value_p[]) {

	// Todo 五、映射变量.

	val_1 = value_p[0];
	val_2 = value_p[1];
	val_3 = value_p[2];
}

int processing(Mat& img) {
	// Todo 六、此处写图像算法.  提示:训练区域坐标为 Point类型的 Point_A(左上) 和 Point_B(右下)

	cvtColor(img, img, cv::COLOR_BGR2GRAY);




	cout << "--> C++ Output Imagr <--" << endl;

	return -1;
}





