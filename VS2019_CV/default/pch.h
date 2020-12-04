// pch.h: 这是预编译标头文件。
// 下方列出的文件仅编译一次，提高了将来生成的生成性能。
// 这还将影响 IntelliSense 性能，包括代码完成和许多代码浏览功能。
// 但是，如果此处列出的文件中的任何一个在生成之间有更新，它们全部都将被重新编译。
// 请勿在此处添加要频繁更新的文件，这将使得性能优势无效。

#ifndef PCH_H
#define PCH_H
#include "opencv2/opencv.hpp"
using namespace cv;
using namespace std;

int result = 0;
Point Point_A = Point(0, 0), Point_B = Point(0, 0);

int processing(Mat& img);

extern "C" __declspec(dllexport) void updateArgs(int   value_p[]);

extern "C" __declspec(dllexport) void updateCoord(int   value_p[4]) {

	Point_A = Point(value_p[0], value_p[1]);
	Point_B = Point(value_p[2], value_p[3]);
}

extern "C" __declspec(dllexport) int getResults(uchar* frame_data, int height, int width, int channels) {
	// *uchar -> Mat

	cv::Mat src(height, width, CV_8UC3, frame_data);
	//图像处理
	result = processing(src);
	cout << "--> C++ Output Imagr <--" << endl;

	if (src.channels() == 1) {
		cvtColor(src, src, cv::COLOR_GRAY2BGR);
	}

	//类型转换 mat -> *uchar 
	int nl = width * channels;
	uchar* inData;
	for (int k = 0, n = 0; k < height; k++) {
		// 每一行图像的指针  
		inData = src.ptr<uchar>(k);
		for (int i = 0; i < nl; i++, n++) {
			frame_data[n] = inData[i];
		}
	}
	return result;
}
#endif //PCH_H
