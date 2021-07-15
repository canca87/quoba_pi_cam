#!/bin/bash 

echo "Starting test dump" 
cd ~ 
source ~/.virtualenvs/cv/bin/activate 
echo "venv started" 
raspivid -md 0 -o automode.h264 -t 30000 -lev 4.2
echo "done automode video" 
raspistill -md 0 -o automode.png -e png 
echo "done automode still" 
#raspivid -md 1 -fps 30 -o mode1_fps30.h264 -t 30000 -lev 4.2
raspivid -md 1 -o mode1.h264 -t 30000 -lev 4.2
echo "done mode1 video" 
raspistill -md 1 -o mode1.png -e png 
echo "done mode1 still" 
#raspivid -md 2 -fps 15 -o mode2_fps15.h264 -t 10000 -lev 4.2
raspivid -md 2 -o mode2.h264 -t 30000 -lev 4.2
echo "done mode2 video"
raspistill -md 2 -o mode2.png -e png 
echo "done mode2 still" 
#raspivid -md 3 -fps 1 -o mode3_fps1.h264 -t 10000 -lev 4.2
raspivid -md 3 -fps 1 -o mode3.h264 -t 30000 -lev 4.2
echo "done mode3 video" 
raspistill -md 3 -o mode3.png -e png 
echo "done mode3 still" 
#raspivid -md 4 -fps 42 -o mode4_fps42.h264 -t 10000 -lev 4.2
raspivid -md 4 -o mode4.h264 -t 30000 -lev 4.2
echo "done mode4 video" 
raspistill -md 4 -o mode4.png -e png 
echo "done mode4 still" 
#raspivid -md 5 -fps 49 -o mode5_fps49.h264 -t 10000 -lev 4.2
raspivid -md 5 -o mode5.h264 -t 30000 -lev 4.2
echo "done mode5 video" 
raspistill -md 5 -o mode5.png -e png 
echo "done mode5 still" 
raspivid -md 6 -o mode6.h264 -t 30000 -lev 4.2
echo "done mode6 video" 
raspistill -md 6 -o mode6.png -e png 
echo "done mode6 still" 
raspivid -md 7 -o mode7.h264 -t 30000 -lev 4.2
echo "done mode7 video" 
raspistill -md 7 -o mode7.png -e png 
echo "done mode7 still" 

cd ~/dev 

echo "moving to dev dir" 

python ~/dev/dump_data.py -> "/home/quoba/dat.txt" 

echo "done sensor data dump" 
