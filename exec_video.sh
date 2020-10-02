#!/bin/bash
python3 main.py -m model/person-detection-retail-0013/person-detection-retail-0013.xml \
	-i resources/Pedestrain_Detect_2_1_1.mp4 \
	-d CPU \
	-c BLUE \
	-at 26.0 \
	| ffmpeg \
	-v warning \
	-f rawvideo \
	-pixel_format bgr24 \
	-video_size 768x432 \
	-framerate 24 \
	-i - http://0.0.0.0:8090/fac.ffm
