#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M")

fswebcam -r 1280x720 /home/pi/MFRC522-python/webcam/$DATE.jpg
