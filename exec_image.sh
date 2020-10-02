#!/bin/bash
python3 main.py -m model/person-detection-retail-0013/person-detection-retail-0013.xml \
	-i resources/family.jpg \
	-d CPU \
	-pt 0.6 \
	| ffmpeg \
	-v warning \
	-f rawvideo \
	-pixel_format bgr24 \
	-video_size 1269x710 \
	-framerate 24 \
	-i - http://0.0.0.0:8090/fac.ffm
