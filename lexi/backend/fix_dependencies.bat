@echo off
echo Fixing Python dependencies...
pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless
pip uninstall -y numpy
pip install numpy==1.24.3
pip install opencv-python==4.8.0.74
echo Dependencies fixed!
pause
