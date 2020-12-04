#ifndef PCH_H
#define PCH_H
#include "opencv.hpp"

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

extern "C" __declspec(dllexport) int getResults(uchar * frame_data, int height, int width, int channels) {
	// *uchar -> Mat

	cv::Mat src(height, width, CV_8UC3, frame_data);
	//图像处理
	result = processing(src);
	cout << "--> Dll Output Imagr <--" << endl;

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
